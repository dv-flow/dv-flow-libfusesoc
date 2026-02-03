#****************************************************************************
#* test_fusesoc_tasks.py
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
from dv_flow.mgr.task_data import TaskDataInput
from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams


@pytest.mark.asyncio
async def test_core_resolve_task(isolated_fusesoc_workspace, test_cores_dir):
    """Test CoreResolve task with isolated FuseSoC workspace"""
    workspace = isolated_fusesoc_workspace
    
    # Setup test core
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if not test_core.exists():
        pytest.skip("Test core files not found")
    
    workspace.add_test_core(test_core, test_sources)
    
    # Create task parameters
    params = CoreResolveParams(
        core="test:cores:simple:1.0",
        target="sim",
        libraries={"test": str(workspace.workspace)}
    )
    
    # Create task input
    task_input = TaskDataInput(
        name="CoreResolve",
        changed=True,
        srcdir=str(workspace.tmp_path),
        rundir=str(workspace.tmp_path / "run"),
        params=params,
        inputs=[],
        memento=None
    )
    
    # Run task
    result = await CoreResolve(None, task_input)
    
    # Verify result
    assert result.status == 0, f"Task should succeed: {[m.msg for m in result.markers]}"
    assert len(result.output) == 1
    
    output = result.output[0]
    assert output['core_name'] == 'test:cores:simple:1.0'
    assert len(output['files']) >= 1
    assert 'core_root' in output
    
    # Check markers
    assert len(result.markers) >= 1
    assert any('Resolved core' in m.msg for m in result.markers)


@pytest.mark.asyncio
async def test_core_resolve_with_nonexistent_core(isolated_fusesoc_workspace):
    """Test CoreResolve task with non-existent core"""
    workspace = isolated_fusesoc_workspace
    
    # Try to resolve non-existent core
    params = CoreResolveParams(
        core="nonexistent:core:name:1.0",
        libraries={"test": str(workspace.workspace)}
    )
    
    task_input = TaskDataInput(
        name="CoreResolve",
        changed=True,
        srcdir=str(workspace.tmp_path),
        rundir=str(workspace.tmp_path / "run"),
        params=params,
        inputs=[],
        memento=None
    )
    
    # Run task
    result = await CoreResolve(None, task_input)
    
    # Should fail gracefully
    assert result.status != 0
    assert len(result.markers) > 0
    assert any(m.severity.value == 'error' for m in result.markers)


@pytest.mark.asyncio  
async def test_core_resolve_caching(isolated_fusesoc_workspace, test_cores_dir):
    """Test that CoreResolve task creates memento for caching"""
    workspace = isolated_fusesoc_workspace
    
    test_core = test_cores_dir / "simple.core"
    test_sources = [
        test_cores_dir / "simple.v",
        test_cores_dir / "simple_tb.v"
    ]
    
    if not test_core.exists():
        pytest.skip("Test core files not found")
    
    workspace.add_test_core(test_core, test_sources)
    
    params = CoreResolveParams(
        core="test:cores:simple:1.0",
        target="sim",
        libraries={"test": str(workspace.workspace)}
    )
    
    task_input = TaskDataInput(
        name="CoreResolve",
        changed=True,
        srcdir=str(workspace.tmp_path),
        rundir=str(workspace.tmp_path / "run"),
        params=params,
        inputs=[],
        memento=None
    )
    
    # First run
    result = await CoreResolve(None, task_input)
    
    assert result.status == 0
    assert result.memento is not None
    assert 'core' in result.memento
    assert result.memento['core'] == params.core
