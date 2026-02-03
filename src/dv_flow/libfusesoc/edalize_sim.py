#****************************************************************************
#* edalize_sim.py
#*
#* Copyright 2023-2025 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*  
#*   http://www.apache.org/licenses/LICENSE-2.0
#*  
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#****************************************************************************
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dv_flow.mgr.task_data import TaskDataInput, TaskDataResult, TaskMarker, SeverityE

from .edam_builder import EdamBuilder
from .edalize_backend import create_sim_backend


class SimConfigureParams(BaseModel):
    """
    Parameters for SimConfigure task.
    
    Configures a simulation using Edalize.
    """
    # Core information (typically from CoreResolve output)
    core_name: str = Field(description="Name of the design")
    files: List[Dict] = Field(description="File list from core resolution")
    include_dirs: List[str] = Field(default_factory=list, description="Include directories")
    
    # Simulation configuration
    toplevel: str = Field(description="Toplevel module name")
    tool: str = Field(default="icarus", description="Simulation tool (icarus, verilator, etc.)")
    
    # Parameters
    parameters: Dict = Field(default_factory=dict, description="Build-time parameters")
    plusargs: Dict = Field(default_factory=dict, description="Runtime plusargs")
    
    # Tool options
    tool_options: Dict = Field(default_factory=dict, description="Tool-specific options")


class SimConfigureOutput(BaseModel):
    """
    Output from SimConfigure task.
    """
    work_root: str = Field(description="Edalize work directory")
    tool: str = Field(description="Configured simulation tool")
    configured: bool = Field(description="Configuration success")


class SimBuildParams(BaseModel):
    """
    Parameters for SimBuild task.
    """
    work_root: str = Field(description="Edalize work directory")
    tool: str = Field(description="Simulation tool")


class SimBuildOutput(BaseModel):
    """
    Output from SimBuild task.
    """
    work_root: str = Field(description="Edalize work directory")
    build_success: bool = Field(description="Build success")
    executable: Optional[str] = Field(default=None, description="Path to simulation executable")


class SimRunParams(BaseModel):
    """
    Parameters for SimRun task.
    """
    work_root: str = Field(description="Edalize work directory")
    tool: str = Field(description="Simulation tool")
    
    # Runtime options
    runtime_plusargs: Dict = Field(default_factory=dict, description="Additional runtime plusargs")


class SimRunOutput(BaseModel):
    """
    Output from SimRun task.
    """
    work_root: str = Field(description="Edalize work directory")
    run_success: bool = Field(description="Simulation success")
    log_file: Optional[str] = Field(default=None, description="Path to simulation log")


async def SimConfigure(runner, input: TaskDataInput[SimConfigureParams]) -> TaskDataResult:
    """
    Configure a simulation using Edalize.
    
    Creates EDAM structure and configures the Edalize backend.
    
    Args:
        runner: Task runner context
        input: Task input with SimConfigureParams
        
    Returns:
        TaskDataResult with SimConfigureOutput
    """
    params: SimConfigureParams = input.params
    markers: List[TaskMarker] = []
    
    try:
        # Build EDAM
        builder = EdamBuilder(params.core_name)
        builder.add_files(params.files)
        builder.set_toplevel(params.toplevel)
        builder.set_flow_options({'tool': params.tool})
        
        if params.include_dirs:
            builder.add_include_dirs(params.include_dirs)
        
        if params.parameters:
            builder.add_parameters(params.parameters)
        
        if params.plusargs:
            builder.add_plusargs(params.plusargs)
        
        if params.tool_options:
            builder.set_tool_options(params.tool, params.tool_options)
        
        edam = builder.build()
        
        # Create work directory
        work_root = Path(input.rundir) / "sim_work"
        
        # Create Edalize backend
        backend = create_sim_backend(edam, work_root, verbose=True)
        
        # Configure
        success = backend.configure()
        
        if success:
            markers.append(TaskMarker(
                severity=SeverityE.Info,
                msg=f"Configured {params.tool} simulation for {params.toplevel}"
            ))
        else:
            markers.append(TaskMarker(
                severity=SeverityE.Error,
                msg=f"Failed to configure {params.tool} simulation"
            ))
        
        output = SimConfigureOutput(
            work_root=str(work_root),
            tool=params.tool,
            configured=success
        )
        
        return TaskDataResult(
            changed=True,
            output=[output.model_dump()],
            markers=markers,
            status=0 if success else 1
        )
        
    except Exception as e:
        markers.append(TaskMarker(
            severity=SeverityE.Error,
            msg=f"Configuration failed: {str(e)}"
        ))
        
        return TaskDataResult(
            changed=False,
            output=[],
            markers=markers,
            status=1
        )


async def SimBuild(runner, input: TaskDataInput[SimBuildParams]) -> TaskDataResult:
    """
    Build simulation executable.
    
    Compiles and elaborates the design using the configured Edalize backend.
    
    Args:
        runner: Task runner context
        input: Task input with SimBuildParams
        
    Returns:
        TaskDataResult with SimBuildOutput
    """
    params: SimBuildParams = input.params
    markers: List[TaskMarker] = []
    
    try:
        work_root = Path(params.work_root)
        
        # Re-create backend (flow was already configured)
        # We need to load the EDAM from the work directory
        from edalize.flows.sim import Sim
        from .edalize_backend import EdalizeBackend
        
        # For now, we'll read the EDAM from the work directory
        # Edalize stores it in work_root
        import json
        edam_file = work_root / f"{params.tool}.edam"
        if not edam_file.exists():
            # Try without tool prefix
            edam_file = work_root / "edam.json"
        
        if edam_file.exists():
            with open(edam_file) as f:
                edam = json.load(f)
        else:
            # Backend will reinitialize from existing files
            edam = {}
        
        backend = EdalizeBackend(Sim, edam, work_root, verbose=True)
        
        # Build
        build_success, build_msg = backend.build()
        
        if build_success:
            markers.append(TaskMarker(
                severity=SeverityE.Info,
                msg=f"Build completed successfully"
            ))
        else:
            markers.append(TaskMarker(
                severity=SeverityE.Error,
                msg=f"Build failed: {build_msg}"
            ))
        
        output = SimBuildOutput(
            work_root=str(work_root),
            build_success=build_success,
            executable=None  # TODO: Determine executable path
        )
        
        return TaskDataResult(
            changed=True,
            output=[output.model_dump()],
            markers=markers,
            status=0 if build_success else 1
        )
        
    except Exception as e:
        markers.append(TaskMarker(
            severity=SeverityE.Error,
            msg=f"Build failed: {str(e)}"
        ))
        
        return TaskDataResult(
            changed=False,
            output=[],
            markers=markers,
            status=1
        )


async def SimRun(runner, input: TaskDataInput[SimRunParams]) -> TaskDataResult:
    """
    Run simulation.
    
    Executes the built simulation model.
    
    Args:
        runner: Task runner context
        input: Task input with SimRunParams
        
    Returns:
        TaskDataResult with SimRunOutput
    """
    params: SimRunParams = input.params
    markers: List[TaskMarker] = []
    
    try:
        work_root = Path(params.work_root)
        
        # Re-create backend
        from edalize.flows.sim import Sim
        from .edalize_backend import EdalizeBackend
        
        backend = EdalizeBackend(Sim, {}, work_root, verbose=True)
        
        # Run
        run_success, run_msg = backend.run()
        
        if run_success:
            markers.append(TaskMarker(
                severity=SeverityE.Info,
                msg="Simulation completed successfully"
            ))
        else:
            markers.append(TaskMarker(
                severity=SeverityE.Error,
                msg=f"Simulation failed: {run_msg}"
            ))
        
        # Look for log files
        log_files = backend.get_log_files()
        log_file = str(log_files[0]) if log_files else None
        
        output = SimRunOutput(
            work_root=str(work_root),
            run_success=run_success,
            log_file=log_file
        )
        
        return TaskDataResult(
            changed=True,
            output=[output.model_dump()],
            markers=markers,
            status=0 if run_success else 1
        )
        
    except Exception as e:
        markers.append(TaskMarker(
            severity=SeverityE.Error,
            msg=f"Simulation failed: {str(e)}"
        ))
        
        return TaskDataResult(
            changed=False,
            output=[],
            markers=markers,
            status=1
        )
