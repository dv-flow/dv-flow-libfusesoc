#****************************************************************************
#* fusesoc_core_resolve.py
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
import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dv_flow.mgr.task_data import TaskDataInput, TaskDataResult, TaskMarker, SeverityE

from .fusesoc_manager import FuseSoCManager
from .fusesoc_fileset import FilesetConverter


class CoreResolveParams(BaseModel):
    """
    Parameters for CoreResolve task.
    
    Resolves a FuseSoC core and extracts file lists.
    """
    # Core identification
    core: str = Field(description="Core VLNV (vendor:library:name:version)")
    
    # Optional filters
    target: Optional[str] = Field(default=None, description="Target configuration (e.g., 'sim', 'synth')")
    tool: Optional[str] = Field(default=None, description="Tool name for tool-specific filesets")
    
    # Library management
    libraries: Dict[str, str] = Field(default_factory=dict, description="Additional libraries to add {name: path}")
    
    # Workspace configuration
    workspace: Optional[str] = Field(default=None, description="FuseSoC workspace directory")


class CoreResolveOutput(BaseModel):
    """
    Output from CoreResolve task.
    
    Contains resolved core information and file lists.
    """
    core_name: str = Field(description="Resolved core name")
    core_root: str = Field(description="Core root directory")
    files_root: str = Field(description="Files root directory (for fetched files)")
    files: List[Dict] = Field(default_factory=list, description="Converted file list")
    dependencies: List[str] = Field(default_factory=list, description="Core dependencies")
    parameters: Dict = Field(default_factory=dict, description="Core parameters")
    include_dirs: List[str] = Field(default_factory=list, description="Include directories")


class CoreResolveMemento(BaseModel):
    """
    Memento for CoreResolve task.
    
    Caches resolved core information.
    """
    core: str
    target: Optional[str]
    tool: Optional[str]
    core_name: str
    last_resolution: float  # Timestamp


async def CoreResolve(runner, input: TaskDataInput[CoreResolveParams]) -> TaskDataResult:
    """
    Resolve a FuseSoC core and extract file lists.
    
    This task:
    1. Initializes FuseSoC in the specified workspace
    2. Adds any additional libraries
    3. Resolves the specified core
    4. Extracts and converts file lists
    5. Returns file information for downstream tasks
    
    Args:
        runner: Task runner context
        input: Task input with CoreResolveParams
        
    Returns:
        TaskDataResult with CoreResolveOutput
    """
    params: CoreResolveParams = input.params
    markers: List[TaskMarker] = []
    
    try:
        # Determine workspace
        workspace = Path(params.workspace) if params.workspace else Path(input.rundir) / "fusesoc_workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize FuseSoC manager
        manager = FuseSoCManager()
        
        # Add libraries
        for lib_name, lib_path in params.libraries.items():
            manager.add_library(lib_name, Path(lib_path))
        
        # Build flags dictionary
        flags = {}
        if params.target:
            flags['target'] = params.target
        if params.tool:
            flags['tool'] = params.tool
        
        # Resolve core
        core = manager.resolve_core(params.core, flags=flags)
        
        markers.append(TaskMarker(
            severity=SeverityE.Info,
            msg=f"Resolved core: {core.name}"
        ))
        
        # Get core files
        core_files = manager.get_core_files(core, flags=flags)
        
        # Convert files to DV Flow format
        converter = FilesetConverter(
            core_root=Path(core_files['core_root']),
            files_root=Path(core_files['files_root'])
        )
        converted_files = converter.convert_files(core_files['files'])
        include_dirs = converter.extract_include_dirs(core_files['files'])
        
        markers.append(TaskMarker(
            severity=SeverityE.Info,
            msg=f"Extracted {len(converted_files)} files from core"
        ))
        
        # Get dependencies
        dependencies = manager.get_dependencies(core, flags=flags)
        
        # Create output
        output = CoreResolveOutput(
            core_name=core_files['name'],
            core_root=core_files['core_root'],
            files_root=core_files['files_root'],
            files=converted_files,
            dependencies=dependencies,
            parameters=core_files.get('parameters', {}),
            include_dirs=include_dirs
        )
        
        # Create memento for caching
        import time
        memento = CoreResolveMemento(
            core=params.core,
            target=params.target,
            tool=params.tool,
            core_name=core_files['name'],
            last_resolution=time.time()
        )
        
        return TaskDataResult(
            changed=True,
            output=[output.model_dump()],
            memento=memento.model_dump(),
            markers=markers,
            status=0
        )
        
    except Exception as e:
        markers.append(TaskMarker(
            severity=SeverityE.Error,
            msg=f"Core resolution failed: {str(e)}"
        ))
        
        return TaskDataResult(
            changed=False,
            output=[],
            markers=markers,
            status=1
        )
