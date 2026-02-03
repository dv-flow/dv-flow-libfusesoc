#****************************************************************************
#* edam_builder.py
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
from typing import Dict, List, Optional, Any


class EdamBuilder:
    """
    Builds EDAM (EDA Metadata) structures for Edalize.
    
    EDAM is the data structure that Edalize uses to describe all inputs
    needed for EDA tool operations (simulation, synthesis, etc.).
    """
    
    def __init__(self, name: str):
        """
        Initialize EDAM builder.
        
        Args:
            name: Project/design name
        """
        self.edam = {
            'name': name,
            'files': [],
            'parameters': {},
            'tool_options': {},
            'flow_options': {},
            'toplevel': [],
        }
        
    def add_files(self, files: List[Dict]) -> 'EdamBuilder':
        """
        Add files to EDAM.
        
        Args:
            files: List of file dictionaries with 'name' and 'file_type'
            
        Returns:
            Self for chaining
        """
        for file_info in files:
            edam_file = {
                'name': str(file_info.get('path', file_info.get('name'))),
                'file_type': self._map_file_type(file_info.get('type', 'user')),
            }
            
            # Add optional attributes
            if file_info.get('is_include'):
                edam_file['is_include_file'] = True
                
            if file_info.get('include_path'):
                edam_file['include_path'] = str(file_info['include_path'])
                
            if file_info.get('library'):
                edam_file['logical_name'] = file_info['library']
                
            self.edam['files'].append(edam_file)
            
        return self
        
    def set_toplevel(self, toplevel: str) -> 'EdamBuilder':
        """
        Set toplevel module(s).
        
        Args:
            toplevel: Toplevel module name (string for Edalize compatibility)
            
        Returns:
            Self for chaining
        """
        # Edalize expects a string, not a list
        if isinstance(toplevel, list):
            self.edam['toplevel'] = toplevel[0] if toplevel else ""
        else:
            self.edam['toplevel'] = str(toplevel)
        return self
        
    def add_parameters(self, parameters: Dict[str, Any]) -> 'EdamBuilder':
        """
        Add parameters (Verilog defines, VHDL generics, plusargs).
        
        Args:
            parameters: Dictionary of parameter names to values
            
        Returns:
            Self for chaining
        """
        for name, value in parameters.items():
            if isinstance(value, dict):
                # Already in EDAM format with datatype, paramtype
                self.edam['parameters'][name] = value
            else:
                # Simple value, infer type
                self.edam['parameters'][name] = {
                    'datatype': self._infer_datatype(value),
                    'default': value,
                    'paramtype': 'vlogparam',  # Default to Verilog parameter
                }
        return self
        
    def add_plusargs(self, plusargs: Dict[str, Any]) -> 'EdamBuilder':
        """
        Add runtime plusargs.
        
        Args:
            plusargs: Dictionary of plusarg names to values
            
        Returns:
            Self for chaining
        """
        for name, value in plusargs.items():
            self.edam['parameters'][name] = {
                'datatype': self._infer_datatype(value),
                'default': value,
                'paramtype': 'plusarg',
            }
        return self
        
    def set_tool_options(self, tool: str, options: Dict[str, Any]) -> 'EdamBuilder':
        """
        Set tool-specific options.
        
        Args:
            tool: Tool name (e.g., 'icarus', 'verilator')
            options: Dictionary of tool options
            
        Returns:
            Self for chaining
        """
        if tool not in self.edam['tool_options']:
            self.edam['tool_options'][tool] = {}
        self.edam['tool_options'][tool].update(options)
        return self
        
    def set_flow_options(self, options: Dict[str, Any]) -> 'EdamBuilder':
        """
        Set flow-level options.
        
        Args:
            options: Dictionary of flow options (e.g., {'tool': 'icarus', 'target': 'sim'})
            
        Returns:
            Self for chaining
        """
        self.edam['flow_options'].update(options)
        return self
        
    def add_include_dirs(self, include_dirs: List[str]) -> 'EdamBuilder':
        """
        Add include directories (convenience method).
        
        Args:
            include_dirs: List of include directory paths
            
        Returns:
            Self for chaining
        """
        # Edalize handles include dirs via tool options
        # For Icarus and Verilator, we need to add them to appropriate tool options
        for tool in ['icarus', 'verilator']:
            if tool not in self.edam['tool_options']:
                self.edam['tool_options'][tool] = {}
                
            if tool == 'icarus':
                if 'iverilog_options' not in self.edam['tool_options'][tool]:
                    self.edam['tool_options'][tool]['iverilog_options'] = []
                for inc_dir in include_dirs:
                    self.edam['tool_options'][tool]['iverilog_options'].extend(['-I', str(inc_dir)])
                    
            elif tool == 'verilator':
                if 'verilator_options' not in self.edam['tool_options'][tool]:
                    self.edam['tool_options'][tool]['verilator_options'] = []
                for inc_dir in include_dirs:
                    self.edam['tool_options'][tool]['verilator_options'].append(f'-I{inc_dir}')
                    
        return self
        
    def build(self) -> Dict:
        """
        Build and return the EDAM structure.
        
        Returns:
            Complete EDAM dictionary
        """
        # Validate required fields
        if not self.edam.get('name'):
            raise ValueError("EDAM 'name' is required")
            
        return self.edam
        
    def _map_file_type(self, dv_flow_type: str) -> str:
        """Map DV Flow file type to EDAM file type."""
        type_map = {
            'verilog': 'verilogSource',
            'systemverilog': 'systemVerilogSource',
            'vhdl': 'vhdlSource',
            'vhdl-2008': 'vhdlSource-2008',
            'constraint': 'user',  # Will need more specific mapping based on tool
            'xdc': 'xdc',
            'sdc': 'SDC',
            'ucf': 'UCF',
            'tcl': 'tclSource',
            'user': 'user',
        }
        return type_map.get(dv_flow_type, 'user')
        
    def _infer_datatype(self, value: Any) -> str:
        """Infer EDAM datatype from Python value."""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'real'
        else:
            return 'str'


def build_edam_from_core(core_files: Dict, toplevel: str, 
                         tool: str = 'icarus', 
                         parameters: Optional[Dict] = None,
                         plusargs: Optional[Dict] = None) -> Dict:
    """
    Convenience function to build EDAM from FuseSoC core files.
    
    Args:
        core_files: Dictionary from FuseSoCManager.get_core_files()
        toplevel: Toplevel module name
        tool: Target tool (default: 'icarus')
        parameters: Optional build-time parameters
        plusargs: Optional runtime plusargs
        
    Returns:
        Complete EDAM dictionary
    """
    from .fusesoc_fileset import FilesetConverter
    
    # Convert files
    converter = FilesetConverter(
        core_root=Path(core_files['core_root']),
        files_root=Path(core_files['files_root'])
    )
    converted_files = converter.convert_files(core_files['files'])
    include_dirs = converter.extract_include_dirs(core_files['files'])
    
    # Build EDAM
    builder = EdamBuilder(core_files['name'])
    builder.add_files(converted_files)
    builder.set_toplevel(toplevel)
    builder.set_flow_options({'tool': tool})
    
    if include_dirs:
        builder.add_include_dirs(include_dirs)
        
    if parameters:
        builder.add_parameters(parameters)
        
    if plusargs:
        builder.add_plusargs(plusargs)
        
    return builder.build()
