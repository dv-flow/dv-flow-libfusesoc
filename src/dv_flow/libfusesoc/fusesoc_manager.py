#****************************************************************************
#* fusesoc_manager.py
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
from fusesoc.coremanager import CoreManager
from fusesoc.librarymanager import LibraryManager
from fusesoc.config import Config


class FuseSoCManager:
    """
    Wrapper around FuseSoC's CoreManager and LibraryManager.
    Provides isolated workspace management for DV Flow integration.
    """
    
    def __init__(self, config_dir: Optional[Path] = None, data_dir: Optional[Path] = None):
        """
        Initialize FuseSoC manager with optional isolated directories.
        
        Args:
            config_dir: Directory for FuseSoC configuration
            data_dir: Directory for FuseSoC data (cores, cache)
        """
        self.config_dir = Path(config_dir) if config_dir else None
        self.data_dir = Path(data_dir) if data_dir else None
        
        # Initialize FuseSoC configuration
        self._config = self._init_config()
        self._library_manager = LibraryManager(self._config)
        self._core_manager = None
        
    def _init_config(self) -> Config:
        """Initialize FuseSoC configuration with isolated paths"""
        # If isolated directories specified, pass config file path to Config
        if self.config_dir:
            config_file = self.config_dir / "fusesoc" / "fusesoc.conf"
            # Config reads the file automatically in __init__
            config = Config(path=str(config_file))
        else:
            # Use default FuseSoC config locations
            config = Config()
                
        return config
        
    def get_core_manager(self) -> CoreManager:
        """Get or create CoreManager instance"""
        if self._core_manager is None:
            self._core_manager = CoreManager(self._config, self._library_manager)
        return self._core_manager
        
    def add_library(self, name: str, path: Path, sync_uri: Optional[str] = None):
        """
        Add a core library to the manager.
        
        Args:
            name: Library name
            path: Local path to library
            sync_uri: Optional remote URI for library sync
        """
        from fusesoc.librarymanager import Library
        
        library = Library(
            name=name,
            location=str(path),
            sync_type="local" if not sync_uri else "git",
            sync_uri=sync_uri,
            auto_sync=False
        )
        self._library_manager.add_library(library)
        
        # Discover cores in the library
        core_manager = self.get_core_manager()
        found_cores = core_manager.find_cores(library, self._config.ignored_dirs)
        
        # Add found cores to database
        for core in found_cores:
            core_manager.db.add(core, library)
        
    def resolve_core(self, core_name: str, flags: Optional[Dict] = None):
        """
        Resolve a core by name/VLNV.
        
        Args:
            core_name: Core name in VLNV format (vendor:library:name:version)
            flags: Optional flags for core resolution (e.g., tool, target)
            
        Returns:
            Resolved core object with file lists and metadata
        """
        from fusesoc.vlnv import Vlnv
        
        core_manager = self.get_core_manager()
        flags = flags or {}
        
        # Parse and resolve the core
        vlnv = Vlnv(core_name)
        core = core_manager.get_core(vlnv)
        
        # Fetch remote dependencies if needed
        if hasattr(core, 'provider') and core.provider:
            if core.provider.status() != 'downloaded':
                core.provider.fetch()
        
        return core
        
    def get_core_files(self, core, flags: Optional[Dict] = None):
        """
        Get file lists from a resolved core.
        
        Args:
            core: Resolved core object
            flags: Optional flags for target selection (e.g., {'tool': 'icarus', 'target': 'sim'})
            
        Returns:
            Dictionary containing file lists with attributes, include directories, and metadata
        """
        flags = flags or {}
        
        # Get files with their attributes from the core
        files = core.get_files(flags)
        
        # Extract dependencies
        dependencies = []
        if hasattr(core, 'get_depends'):
            dependencies = [str(dep) for dep in core.get_depends(flags)]
        
        # Get parameters if available
        parameters = {}
        if hasattr(core, 'get_parameters'):
            parameters = core.get_parameters(flags)
        
        return {
            'files': files,
            'name': str(core.name),
            'core_root': core.core_root,
            'files_root': core.files_root,
            'dependencies': dependencies,
            'parameters': parameters,
        }
        
    def get_dependencies(self, core, flags: Optional[Dict] = None):
        """
        Get dependency tree for a core.
        
        Args:
            core: Resolved core object
            flags: Optional flags for dependency resolution
            
        Returns:
            List of dependent cores
        """
        core_manager = self.get_core_manager()
        flags = flags or {}
        
        # Get direct dependencies
        if hasattr(core, 'get_depends'):
            depends = core.get_depends(flags)
            return [str(dep) for dep in depends]
        
        return []
    
    def resolve_dependencies(self, core_name: str, flags: Optional[Dict] = None):
        """
        Recursively resolve all dependencies for a core.
        
        Args:
            core_name: Core name in VLNV format
            flags: Optional flags for resolution
            
        Returns:
            List of all resolved cores including dependencies
        """
        from fusesoc.vlnv import Vlnv
        
        core_manager = self.get_core_manager()
        flags = flags or {}
        
        vlnv = Vlnv(core_name)
        
        # Use FuseSoC's dependency resolution
        cores = core_manager.get_depends(vlnv, flags)
        
        return cores
