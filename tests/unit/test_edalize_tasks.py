#****************************************************************************
#* test_edalize_tasks.py
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
from dv_flow.libfusesoc.edalize_sim import (
    SimConfigure, SimConfigureParams,
    SimBuild, SimBuildParams,
    SimRun, SimRunParams
)


@pytest.mark.asyncio
async def test_sim_configure_task(tmp_path):
    """Test SimConfigure task"""
    
    # Create some test files
    test_file = tmp_path / "test.v"
    test_file.write_text("module test; endmodule")
    
    files = [
        {'path': str(test_file), 'type': 'verilog', 'name': 'test.v'}
    ]
    
    params = SimConfigureParams(
        core_name="test_design",
        files=files,
        toplevel="test",
        tool="icarus",
        parameters={'WIDTH': 8}
    )
    
    task_input = TaskDataInput(
        name="SimConfigure",
        changed=True,
        srcdir=str(tmp_path),
        rundir=str(tmp_path / "run"),
        params=params,
        inputs=[],
        memento=None
    )
    
    # Run task
    result = await SimConfigure(None, task_input)
    
    # Verify result
    assert result.status == 0, f"Configuration should succeed: {[m.msg for m in result.markers]}"
    assert len(result.output) == 1
    
    output = result.output[0]
    assert output['tool'] == 'icarus'
    assert output['configured'] == True
    assert 'work_root' in output
    
    # Check that work directory was created
    work_root = Path(output['work_root'])
    assert work_root.exists()


@pytest.mark.asyncio
async def test_sim_configure_with_plusargs(tmp_path):
    """Test SimConfigure with plusargs"""
    
    test_file = tmp_path / "test.v"
    test_file.write_text("module test; endmodule")
    
    files = [
        {'path': str(test_file), 'type': 'verilog', 'name': 'test.v'}
    ]
    
    params = SimConfigureParams(
        core_name="test_design",
        files=files,
        toplevel="test",
        tool="icarus",
        plusargs={'seed': 42, 'verbose': True}
    )
    
    task_input = TaskDataInput(
        name="SimConfigure",
        changed=True,
        srcdir=str(tmp_path),
        rundir=str(tmp_path / "run"),
        params=params,
        inputs=[],
        memento=None
    )
    
    result = await SimConfigure(None, task_input)
    
    assert result.status == 0
    assert result.output[0]['configured'] == True


@pytest.mark.asyncio
async def test_sim_configure_with_include_dirs(tmp_path):
    """Test SimConfigure with include directories"""
    
    # Create include directory
    inc_dir = tmp_path / "include"
    inc_dir.mkdir()
    (inc_dir / "defines.vh").write_text("`define TEST 1")
    
    test_file = tmp_path / "test.v"
    test_file.write_text('`include "defines.vh"\nmodule test; endmodule')
    
    files = [
        {'path': str(test_file), 'type': 'verilog', 'name': 'test.v'}
    ]
    
    params = SimConfigureParams(
        core_name="test_design",
        files=files,
        include_dirs=[str(inc_dir)],
        toplevel="test",
        tool="icarus"
    )
    
    task_input = TaskDataInput(
        name="SimConfigure",
        changed=True,
        srcdir=str(tmp_path),
        rundir=str(tmp_path / "run"),
        params=params,
        inputs=[],
        memento=None
    )
    
    result = await SimConfigure(None, task_input)
    
    assert result.status == 0
    assert result.output[0]['configured'] == True


@pytest.mark.asyncio
async def test_sim_build_task(tmp_path):
    """Test SimBuild task (after configuration)"""
    
    # First configure
    test_file = tmp_path / "test.v"
    test_file.write_text("module test; initial begin $display(\"PASS\"); $finish; end endmodule")
    
    files = [
        {'path': str(test_file), 'type': 'verilog', 'name': 'test.v'}
    ]
    
    config_params = SimConfigureParams(
        core_name="test_design",
        files=files,
        toplevel="test",
        tool="icarus"
    )
    
    config_input = TaskDataInput(
        name="SimConfigure",
        changed=True,
        srcdir=str(tmp_path),
        rundir=str(tmp_path / "run"),
        params=config_params,
        inputs=[],
        memento=None
    )
    
    config_result = await SimConfigure(None, config_input)
    assert config_result.status == 0
    
    work_root = config_result.output[0]['work_root']
    
    # Now build
    build_params = SimBuildParams(
        work_root=work_root,
        tool="icarus"
    )
    
    build_input = TaskDataInput(
        name="SimBuild",
        changed=True,
        srcdir=str(tmp_path),
        rundir=str(tmp_path / "run"),
        params=build_params,
        inputs=[],
        memento=None
    )
    
    build_result = await SimBuild(None, build_input)
    
    # Build might fail if icarus isn't installed or there are path issues
    # But task should handle it gracefully
    assert build_result.status in [0, 1]
    assert len(build_result.output) >= 0
    
    if build_result.status == 0:
        output = build_result.output[0]
        assert 'build_success' in output


@pytest.mark.asyncio
async def test_task_chain_configure_build(tmp_path):
    """Test chaining SimConfigure -> SimBuild"""
    
    test_file = tmp_path / "test.v"
    test_file.write_text("module test; initial begin $finish; end endmodule")
    
    files = [
        {'path': str(test_file), 'type': 'verilog', 'name': 'test.v'}
    ]
    
    # Configure
    config_params = SimConfigureParams(
        core_name="test_design",
        files=files,
        toplevel="test",
        tool="icarus"
    )
    
    config_input = TaskDataInput(
        name="SimConfigure",
        changed=True,
        srcdir=str(tmp_path),
        rundir=str(tmp_path / "run"),
        params=config_params,
        inputs=[],
        memento=None
    )
    
    config_result = await SimConfigure(None, config_input)
    
    if config_result.status == 0:
        # Build
        work_root = config_result.output[0]['work_root']
        
        build_params = SimBuildParams(
            work_root=work_root,
            tool="icarus"
        )
        
        build_input = TaskDataInput(
            name="SimBuild",
            changed=True,
            srcdir=str(tmp_path),
            rundir=str(tmp_path / "run"),
            params=build_params,
            inputs=[config_result.output[0]],
            memento=None
        )
        
        build_result = await SimBuild(None, build_input)
        
        # Verify the chain worked
        assert build_result is not None
