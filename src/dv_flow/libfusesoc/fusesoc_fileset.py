#****************************************************************************
#* fusesoc_fileset.py
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


class FilesetConverter:
    """
    Converts FuseSoC core filesets to DV Flow file collection format.
    Handles file type mapping and attribute conversion.
    """
    
    # Map FuseSoC file types to common categories
    FILE_TYPE_MAP = {
        'verilogSource': 'verilog',
        'systemVerilogSource': 'systemverilog',
        'vhdlSource': 'vhdl',
        'vhdlSource-2008': 'vhdl',
        'tclSource': 'tcl',
        'user': 'user',
        'xdc': 'constraint',
        'SDC': 'constraint',
        'UCF': 'constraint',
        'PCF': 'constraint',
        'LPF': 'constraint',
    }
    
    def __init__(self, core_root: Path, files_root: Optional[Path] = None):
        """
        Initialize fileset converter.
        
        Args:
            core_root: Root directory of the core file
            files_root: Root directory for fetched files (if different from core_root)
        """
        self.core_root = Path(core_root)
        self.files_root = Path(files_root) if files_root else self.core_root
        
    def convert_files(self, fusesoc_files: List[Dict]) -> List[Dict]:
        """
        Convert FuseSoC file list to DV Flow format.
        
        Args:
            fusesoc_files: List of files from FuseSoC core (from core.get_files())
            
        Returns:
            List of file dictionaries in DV Flow format
        """
        converted_files = []
        
        for file_info in fusesoc_files:
            converted = self._convert_file(file_info)
            if converted:
                converted_files.append(converted)
                
        return converted_files
        
    def _convert_file(self, file_info: Dict) -> Optional[Dict]:
        """
        Convert a single file entry from FuseSoC to DV Flow format.
        
        Args:
            file_info: File dictionary from FuseSoC
            
        Returns:
            Converted file dictionary or None if file should be skipped
        """
        filename = file_info.get('name')
        if not filename:
            return None
            
        # Resolve absolute path
        abs_path = self._resolve_file_path(filename)
        
        # Get file type
        file_type = file_info.get('file_type', 'user')
        mapped_type = self.FILE_TYPE_MAP.get(file_type, file_type)
        
        # Build converted entry
        converted = {
            'path': str(abs_path),
            'type': mapped_type,
            'name': filename,
        }
        
        # Copy over relevant attributes
        if 'is_include_file' in file_info:
            converted['is_include'] = file_info['is_include_file']
            
        if 'include_path' in file_info:
            converted['include_path'] = self._resolve_file_path(file_info['include_path'])
            
        if 'logical_name' in file_info:
            converted['library'] = file_info['logical_name']
            
        # Copy any additional attributes
        for key in ['copyto', 'tags']:
            if key in file_info:
                converted[key] = file_info[key]
                
        return converted
        
    def _resolve_file_path(self, filename: str) -> Path:
        """
        Resolve file path relative to core_root or files_root.
        
        Args:
            filename: File path from FuseSoC core
            
        Returns:
            Absolute path to the file
        """
        if os.path.isabs(filename):
            return Path(filename)
            
        # Try core_root first
        core_path = self.core_root / filename
        if core_path.exists():
            return core_path.resolve()
            
        # Try files_root if different
        if self.files_root != self.core_root:
            files_path = self.files_root / filename
            if files_path.exists():
                return files_path.resolve()
                
        # Return core_root path even if doesn't exist (may be generated)
        return core_path.resolve()
        
    def extract_include_dirs(self, fusesoc_files: List[Dict]) -> List[str]:
        """
        Extract include directories from file list.
        
        Args:
            fusesoc_files: List of files from FuseSoC core
            
        Returns:
            List of include directory paths
        """
        include_dirs = set()
        
        for file_info in fusesoc_files:
            # Check for explicit include_path attribute
            if 'include_path' in file_info:
                inc_path = self._resolve_file_path(file_info['include_path'])
                include_dirs.add(str(inc_path))
                
            # Check if file is marked as include file
            if file_info.get('is_include_file', False):
                filename = file_info.get('name')
                if filename:
                    file_path = self._resolve_file_path(filename)
                    include_dirs.add(str(file_path.parent))
                    
        return sorted(list(include_dirs))
        
    def filter_by_type(self, converted_files: List[Dict], file_types: List[str]) -> List[Dict]:
        """
        Filter files by type.
        
        Args:
            converted_files: List of converted file dictionaries
            file_types: List of file types to include
            
        Returns:
            Filtered list of files
        """
        return [f for f in converted_files if f.get('type') in file_types]
        
    def get_source_files(self, converted_files: List[Dict]) -> List[Dict]:
        """
        Get only source files (exclude constraints, scripts, etc).
        
        Args:
            converted_files: List of converted file dictionaries
            
        Returns:
            List of source files
        """
        source_types = ['verilog', 'systemverilog', 'vhdl']
        return self.filter_by_type(converted_files, source_types)
