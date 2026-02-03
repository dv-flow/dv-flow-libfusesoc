#****************************************************************************
#* test_core_resolution.py
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
import pytest
from pathlib import Path
from dv_flow.libfusesoc.fusesoc_manager import FuseSoCManager
from dv_flow.libfusesoc.fusesoc_fileset import FilesetConverter


def test_resolve_simple_core(isolated_fusesoc_workspace, test_cores_dir):
    """Test resolving a simple test core in isolated environment"""
    workspace = isolated_fusesoc_workspace
    
    # Copy test core to workspace
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if not test_core.exists():
        pytest.skip("Test core files not found")
    
    workspace.add_test_core(test_core, test_sources)
    
    # Create manager
    manager = FuseSoCManager(
        config_dir=workspace.config_dir,
        data_dir=workspace.data_dir
    )
    
    # Add workspace as a library
    manager.add_library("test", workspace.workspace)
    
    # Resolve the core
    core = manager.resolve_core("test:cores:simple:1.0")
    
    # Verify core was resolved
    assert core is not None
    assert str(core.name) == "test:cores:simple:1.0"
    
    # Get files for sim target
    core_files = manager.get_core_files(core, flags={'target': 'sim'})
    
    # Verify we got files
    assert 'files' in core_files
    assert len(core_files['files']) > 0
    
    # Verify file paths are within workspace (isolated)
    for file_info in core_files['files']:
        file_path = Path(file_info['name'])
        # Files should be relative or within workspace
        assert not file_path.is_absolute() or str(workspace.workspace) in str(file_path)


def test_convert_core_files(isolated_fusesoc_workspace, test_cores_dir):
    """Test converting FuseSoC core files to DV Flow format"""
    workspace = isolated_fusesoc_workspace
    
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if not test_core.exists():
        pytest.skip("Test core files not found")
    
    workspace.add_test_core(test_core, test_sources)
    
    # Create manager and resolve core
    manager = FuseSoCManager(
        config_dir=workspace.config_dir,
        data_dir=workspace.data_dir
    )
    manager.add_library("test", workspace.workspace)
    
    core = manager.resolve_core("test:cores:simple:1.0")
    core_files = manager.get_core_files(core, flags={'target': 'sim'})
    
    # Convert files using FilesetConverter
    converter = FilesetConverter(
        core_root=Path(core_files['core_root']),
        files_root=Path(core_files['files_root'])
    )
    
    converted_files = converter.convert_files(core_files['files'])
    
    # Verify conversion
    assert len(converted_files) > 0
    
    for file_info in converted_files:
        assert 'path' in file_info
        assert 'type' in file_info
        assert 'name' in file_info
        
        # Verify file paths are absolute
        assert Path(file_info['path']).is_absolute()
        
    # Get just source files
    source_files = converter.get_source_files(converted_files)
    assert len(source_files) > 0
    
    # Should have verilog type files
    assert any(f['type'] in ['verilog', 'systemverilog'] for f in source_files)


def test_core_dependencies(isolated_fusesoc_workspace, test_cores_dir):
    """Test getting core dependencies"""
    workspace = isolated_fusesoc_workspace
    
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if not test_core.exists():
        pytest.skip("Test core files not found")
    
    workspace.add_test_core(test_core, test_sources)
    
    manager = FuseSoCManager(
        config_dir=workspace.config_dir,
        data_dir=workspace.data_dir
    )
    manager.add_library("test", workspace.workspace)
    
    core = manager.resolve_core("test:cores:simple:1.0")
    
    # Get dependencies
    deps = manager.get_dependencies(core, flags={'target': 'sim'})
    
    # Simple core has no dependencies
    assert isinstance(deps, list)
    # For this simple core, should be empty
    # (More complex test would need a core with dependencies)


def test_target_specific_files(isolated_fusesoc_workspace, test_cores_dir):
    """Test that target-specific filesets are respected"""
    workspace = isolated_fusesoc_workspace
    
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if not test_core.exists():
        pytest.skip("Test core files not found")
    
    workspace.add_test_core(test_core, test_sources)
    
    manager = FuseSoCManager(
        config_dir=workspace.config_dir,
        data_dir=workspace.data_dir
    )
    manager.add_library("test", workspace.workspace)
    
    core = manager.resolve_core("test:cores:simple:1.0")
    
    # Get files for different targets
    default_files = manager.get_core_files(core, flags={})
    sim_files = manager.get_core_files(core, flags={'target': 'sim'})
    
    # sim target should include both rtl and tb filesets
    # default target should only include rtl
    assert len(sim_files['files']) >= len(default_files['files'])
