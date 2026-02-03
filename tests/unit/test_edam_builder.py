#****************************************************************************
#* test_edam_builder.py
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
from dv_flow.libfusesoc.edam_builder import EdamBuilder, build_edam_from_core


def test_basic_edam_structure():
    """Test basic EDAM structure creation"""
    builder = EdamBuilder("test_design")
    
    edam = builder.build()
    
    assert edam['name'] == "test_design"
    assert 'files' in edam
    assert 'parameters' in edam
    assert 'tool_options' in edam
    assert 'flow_options' in edam


def test_add_files():
    """Test adding files to EDAM"""
    builder = EdamBuilder("test")
    
    files = [
        {'path': '/path/to/file1.v', 'type': 'verilog'},
        {'path': '/path/to/file2.sv', 'type': 'systemverilog'},
        {'path': '/path/to/file3.vhd', 'type': 'vhdl'},
    ]
    
    builder.add_files(files)
    edam = builder.build()
    
    assert len(edam['files']) == 3
    assert edam['files'][0]['name'] == '/path/to/file1.v'
    assert edam['files'][0]['file_type'] == 'verilogSource'
    assert edam['files'][1]['file_type'] == 'systemVerilogSource'
    assert edam['files'][2]['file_type'] == 'vhdlSource'


def test_set_toplevel():
    """Test setting toplevel module"""
    builder = EdamBuilder("test")
    
    builder.set_toplevel("my_top")
    edam = builder.build()
    
    assert edam['toplevel'] == 'my_top'
    
    # Test with list (takes first element)
    builder2 = EdamBuilder("test2")
    builder2.set_toplevel(['top1', 'top2'])
    edam2 = builder2.build()
    
    assert edam2['toplevel'] == 'top1'


def test_add_parameters():
    """Test adding parameters"""
    builder = EdamBuilder("test")
    
    params = {
        'WIDTH': 8,
        'ENABLE': True,
        'NAME': 'test',
    }
    
    builder.add_parameters(params)
    edam = builder.build()
    
    assert 'WIDTH' in edam['parameters']
    assert edam['parameters']['WIDTH']['datatype'] == 'int'
    assert edam['parameters']['WIDTH']['default'] == 8
    
    assert 'ENABLE' in edam['parameters']
    assert edam['parameters']['ENABLE']['datatype'] == 'bool'
    
    assert 'NAME' in edam['parameters']
    assert edam['parameters']['NAME']['datatype'] == 'str'


def test_add_plusargs():
    """Test adding runtime plusargs"""
    builder = EdamBuilder("test")
    
    plusargs = {
        'seed': 42,
        'verbose': True,
    }
    
    builder.add_plusargs(plusargs)
    edam = builder.build()
    
    assert 'seed' in edam['parameters']
    assert edam['parameters']['seed']['paramtype'] == 'plusarg'
    assert edam['parameters']['seed']['default'] == 42
    
    assert 'verbose' in edam['parameters']
    assert edam['parameters']['verbose']['paramtype'] == 'plusarg'


def test_set_tool_options():
    """Test setting tool-specific options"""
    builder = EdamBuilder("test")
    
    builder.set_tool_options('icarus', {
        'iverilog_options': ['-g2012', '-Wall']
    })
    
    edam = builder.build()
    
    assert 'icarus' in edam['tool_options']
    assert edam['tool_options']['icarus']['iverilog_options'] == ['-g2012', '-Wall']


def test_set_flow_options():
    """Test setting flow-level options"""
    builder = EdamBuilder("test")
    
    builder.set_flow_options({
        'tool': 'verilator',
        'target': 'sim'
    })
    
    edam = builder.build()
    
    assert edam['flow_options']['tool'] == 'verilator'
    assert edam['flow_options']['target'] == 'sim'


def test_add_include_dirs():
    """Test adding include directories"""
    builder = EdamBuilder("test")
    
    include_dirs = ['/path/to/inc1', '/path/to/inc2']
    builder.add_include_dirs(include_dirs)
    
    edam = builder.build()
    
    # Should add to both icarus and verilator options
    assert 'icarus' in edam['tool_options']
    assert 'iverilog_options' in edam['tool_options']['icarus']
    assert '-I' in edam['tool_options']['icarus']['iverilog_options']
    
    assert 'verilator' in edam['tool_options']
    assert 'verilator_options' in edam['tool_options']['verilator']


def test_file_attributes():
    """Test that file attributes are properly converted"""
    builder = EdamBuilder("test")
    
    files = [
        {
            'path': '/path/to/inc.vh',
            'type': 'verilog',
            'is_include': True,
            'include_path': '/path/to'
        },
        {
            'path': '/path/to/pkg.vhd',
            'type': 'vhdl',
            'library': 'work'
        }
    ]
    
    builder.add_files(files)
    edam = builder.build()
    
    assert edam['files'][0]['is_include_file'] == True
    assert edam['files'][0]['include_path'] == '/path/to'
    
    assert edam['files'][1]['logical_name'] == 'work'


def test_builder_chaining():
    """Test that builder methods can be chained"""
    edam = (EdamBuilder("test")
            .add_files([{'path': 'test.v', 'type': 'verilog'}])
            .set_toplevel("top")
            .add_parameters({'WIDTH': 8})
            .set_flow_options({'tool': 'icarus'})
            .build())
    
    assert edam['name'] == "test"
    assert len(edam['files']) == 1
    assert edam['toplevel'] == 'top'
    assert 'WIDTH' in edam['parameters']
    assert edam['flow_options']['tool'] == 'icarus'


def test_build_edam_from_core():
    """Test convenience function for building EDAM from core files"""
    core_files = {
        'name': 'test:core:simple:1.0',
        'core_root': '/path/to/core',
        'files_root': '/path/to/core',
        'files': [
            {'name': 'test.v', 'file_type': 'verilogSource'},
            {'name': 'test_tb.v', 'file_type': 'verilogSource'},
        ],
        'parameters': {},
    }
    
    edam = build_edam_from_core(
        core_files,
        toplevel='test_tb',
        tool='icarus',
        parameters={'WIDTH': 16}
    )
    
    assert edam['name'] == 'test:core:simple:1.0'
    assert len(edam['files']) == 2
    assert edam['toplevel'] == 'test_tb'
    assert edam['flow_options']['tool'] == 'icarus'
    assert 'WIDTH' in edam['parameters']
