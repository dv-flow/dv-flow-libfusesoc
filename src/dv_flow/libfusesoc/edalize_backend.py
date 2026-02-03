#****************************************************************************
#* edalize_backend.py
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
import subprocess
from pathlib import Path
from typing import Dict, Optional, List


class EdalizeBackend:
    """
    Wrapper around Edalize backend/flow instantiation and execution.
    Handles the configure/build/run lifecycle for EDA tools.
    """
    
    def __init__(self, flow_class, edam: Dict, work_root: Path, verbose: bool = False):
        """
        Initialize Edalize backend.
        
        Args:
            flow_class: Edalize flow class (e.g., Sim, Vivado)
            edam: EDAM dictionary
            work_root: Working directory for tool execution
            verbose: Enable verbose output
        """
        self.flow_class = flow_class
        self.edam = edam
        self.work_root = Path(work_root)
        self.verbose = verbose
        self.flow = None
        
        # Create work directory
        self.work_root.mkdir(parents=True, exist_ok=True)
        
    def configure(self) -> bool:
        """
        Configure the flow (setup files, generate scripts).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Instantiate the flow
            self.flow = self.flow_class(
                edam=self.edam,
                work_root=str(self.work_root),
                verbose=self.verbose
            )
            
            # Configure the flow
            self.flow.configure()
            
            return True
            
        except Exception as e:
            print(f"Configuration failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
            
    def build(self, args: Optional[List[str]] = None) -> tuple[bool, str]:
        """
        Build the design (compile, elaborate).
        
        Args:
            args: Optional additional build arguments (deprecated, unused)
            
        Returns:
            Tuple of (success, output)
        """
        if not self.flow:
            return False, "Flow not configured. Call configure() first."
            
        try:
            # Build (Edalize flows don't take args parameter)
            self.flow.build()
            
            # Check for build artifacts
            build_success = self._check_build_success()
            
            return build_success, "Build completed"
            
        except Exception as e:
            error_msg = f"Build failed: {e}"
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False, error_msg
            
    def run(self, args: Optional[List[str]] = None) -> tuple[bool, str]:
        """
        Run the design (simulate, program FPGA, etc.).
        
        Args:
            args: Optional additional run arguments (deprecated, unused)
            
        Returns:
            Tuple of (success, output)
        """
        if not self.flow:
            return False, "Flow not configured. Call configure() first."
            
        try:
            # Run (Edalize flows don't take args parameter)
            self.flow.run()
            
            # Check for success indicators
            run_success = self._check_run_success()
            
            return run_success, "Run completed"
            
        except Exception as e:
            error_msg = f"Run failed: {e}"
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False, error_msg
            
    def get_tool(self) -> Optional[str]:
        """Get the tool name being used."""
        if self.flow:
            return self.edam.get('flow_options', {}).get('tool')
        return None
        
    def get_work_root(self) -> Path:
        """Get the work directory path."""
        return self.work_root
        
    def _check_build_success(self) -> bool:
        """
        Check if build was successful by looking for expected artifacts.
        
        Returns:
            True if build appears successful
        """
        # For simulation, check for executable/model
        tool = self.get_tool()
        
        if tool == 'icarus':
            # Icarus creates simv or <toplevel> executable
            return (self.work_root / 'simv').exists() or \
                   any(self.work_root.glob('*.vvp'))
                   
        elif tool == 'verilator':
            # Verilator creates obj_dir with V<toplevel> executable
            obj_dirs = list(self.work_root.glob('obj_dir'))
            if obj_dirs:
                executables = list(obj_dirs[0].glob('V*'))
                return len(executables) > 0
            return False
            
        # Default: assume success if no exception was raised
        return True
        
    def _check_run_success(self) -> bool:
        """
        Check if run was successful.
        
        Returns:
            True if run appears successful
        """
        # Could check for:
        # - Exit code from simulation
        # - Specific output patterns
        # - Log files
        
        # For now, assume success if no exception
        return True
        
    def get_log_files(self) -> List[Path]:
        """
        Get list of log files generated during build/run.
        
        Returns:
            List of log file paths
        """
        log_files = []
        
        # Common log file patterns
        patterns = ['*.log', '*.rpt', 'transcript']
        
        for pattern in patterns:
            log_files.extend(self.work_root.glob(pattern))
            
        return log_files
        
    def cleanup(self):
        """Clean up work directory."""
        import shutil
        if self.work_root.exists():
            shutil.rmtree(self.work_root)


def create_sim_backend(edam: Dict, work_root: Path, verbose: bool = False) -> EdalizeBackend:
    """
    Convenience function to create a simulation backend.
    
    Args:
        edam: EDAM dictionary
        work_root: Working directory
        verbose: Enable verbose output
        
    Returns:
        EdalizeBackend instance configured for simulation
    """
    from edalize.flows.sim import Sim
    return EdalizeBackend(Sim, edam, work_root, verbose)


def create_fpga_backend(edam: Dict, work_root: Path, verbose: bool = False) -> EdalizeBackend:
    """
    Convenience function to create an FPGA synthesis backend.
    
    Args:
        edam: EDAM dictionary
        work_root: Working directory
        verbose: Enable verbose output
        
    Returns:
        EdalizeBackend instance configured for FPGA synthesis
    """
    from edalize.flows.vivado import Vivado
    return EdalizeBackend(Vivado, edam, work_root, verbose)
