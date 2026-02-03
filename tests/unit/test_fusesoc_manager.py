#****************************************************************************
#* test_fusesoc_manager.py
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
import pytest
from pathlib import Path
from dv_flow.libfusesoc.fusesoc_manager import FuseSoCManager


def test_isolated_workspace_creation(isolated_fusesoc_workspace):
    """Test that isolated workspace is created correctly"""
    workspace = isolated_fusesoc_workspace
    
    # Verify directories were created
    assert workspace.workspace.exists()
    assert workspace.config_dir.exists()
    assert workspace.data_dir.exists()
    
    # Verify environment variables are set to test directories
    assert os.environ['XDG_DATA_HOME'] == str(workspace.data_dir)
    assert os.environ['XDG_CONFIG_HOME'] == str(workspace.config_dir)
    assert os.environ['FUSESOC_CORES_ROOT'] == str(workspace.workspace)
    
    # Verify paths are within tmp_path (isolated)
    assert workspace.workspace.is_relative_to(workspace.tmp_path)
    assert workspace.config_dir.is_relative_to(workspace.tmp_path)
    assert workspace.data_dir.is_relative_to(workspace.tmp_path)


def test_fusesoc_manager_isolated(isolated_fusesoc_workspace):
    """Test FuseSoC manager initialization in isolated environment"""
    workspace = isolated_fusesoc_workspace
    
    # Create manager with isolated directories
    manager = FuseSoCManager(
        config_dir=workspace.config_dir,
        data_dir=workspace.data_dir
    )
    
    # Verify manager was created
    assert manager is not None
    assert manager.config_dir == workspace.config_dir
    assert manager.data_dir == workspace.data_dir


def test_add_test_core(isolated_fusesoc_workspace, test_cores_dir):
    """Test adding a test core to isolated workspace"""
    workspace = isolated_fusesoc_workspace
    
    # Copy test core to workspace
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if test_core.exists():
        dest_core = workspace.add_test_core(test_core, test_sources)
        
        # Verify files were copied to isolated workspace
        assert dest_core.exists()
        assert dest_core.is_relative_to(workspace.workspace)
        
        for src in test_sources:
            dest_src = workspace.workspace / src.name
            assert dest_src.exists()
            assert dest_src.is_relative_to(workspace.workspace)
    else:
        pytest.skip("Test core files not found")


def test_no_global_contamination(isolated_fusesoc_workspace):
    """Verify that test operations don't affect global FuseSoC installation"""
    workspace = isolated_fusesoc_workspace
    
    # Check that standard FuseSoC directories are NOT being used
    home = Path.home()
    global_fusesoc_data = home / ".local" / "share" / "fusesoc"
    global_fusesoc_config = home / ".config" / "fusesoc"
    
    # Verify our workspace is NOT in global locations
    assert not workspace.workspace.is_relative_to(global_fusesoc_data)
    assert not workspace.config_dir.is_relative_to(global_fusesoc_config)
    
    # Verify environment points to test directories, not global ones
    assert str(global_fusesoc_data) not in os.environ.get('XDG_DATA_HOME', '')
    assert str(global_fusesoc_config) not in os.environ.get('XDG_CONFIG_HOME', '')
