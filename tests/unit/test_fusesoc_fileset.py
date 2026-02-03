#****************************************************************************
#* test_fusesoc_fileset.py
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
from dv_flow.libfusesoc.fusesoc_fileset import FilesetConverter


def test_file_type_mapping(tmp_path):
    """Test that FuseSoC file types are mapped correctly"""
    core_root = tmp_path / "core"
    core_root.mkdir()
    
    # Create test files
    (core_root / "test.v").write_text("module test; endmodule")
    (core_root / "test.sv").write_text("module test; endmodule")
    
    converter = FilesetConverter(core_root)
    
    fusesoc_files = [
        {'name': 'test.v', 'file_type': 'verilogSource'},
        {'name': 'test.sv', 'file_type': 'systemVerilogSource'},
    ]
    
    converted = converter.convert_files(fusesoc_files)
    
    assert len(converted) == 2
    assert converted[0]['type'] == 'verilog'
    assert converted[1]['type'] == 'systemverilog'
    assert converted[0]['name'] == 'test.v'
    assert converted[1]['name'] == 'test.sv'


def test_file_path_resolution(tmp_path):
    """Test that file paths are resolved correctly"""
    core_root = tmp_path / "core"
    core_root.mkdir()
    
    test_file = core_root / "rtl" / "test.v"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("module test; endmodule")
    
    converter = FilesetConverter(core_root)
    
    fusesoc_files = [
        {'name': 'rtl/test.v', 'file_type': 'verilogSource'},
    ]
    
    converted = converter.convert_files(fusesoc_files)
    
    assert len(converted) == 1
    assert Path(converted[0]['path']).exists()
    assert Path(converted[0]['path']).is_absolute()
    assert converted[0]['path'].endswith('rtl/test.v')


def test_include_file_handling(tmp_path):
    """Test handling of include files and directories"""
    core_root = tmp_path / "core"
    inc_dir = core_root / "include"
    inc_dir.mkdir(parents=True)
    
    (inc_dir / "defines.vh").write_text("`define TEST 1")
    
    converter = FilesetConverter(core_root)
    
    fusesoc_files = [
        {
            'name': 'include/defines.vh',
            'file_type': 'verilogSource',
            'is_include_file': True
        },
    ]
    
    converted = converter.convert_files(fusesoc_files)
    include_dirs = converter.extract_include_dirs(fusesoc_files)
    
    assert len(converted) == 1
    assert converted[0].get('is_include') == True
    assert len(include_dirs) == 1
    assert 'include' in include_dirs[0]


def test_logical_name_mapping(tmp_path):
    """Test that VHDL logical names are converted to library attribute"""
    core_root = tmp_path / "core"
    core_root.mkdir()
    
    (core_root / "test.vhd").write_text("library work;")
    
    converter = FilesetConverter(core_root)
    
    fusesoc_files = [
        {
            'name': 'test.vhd',
            'file_type': 'vhdlSource',
            'logical_name': 'work'
        },
    ]
    
    converted = converter.convert_files(fusesoc_files)
    
    assert len(converted) == 1
    assert converted[0]['library'] == 'work'


def test_filter_by_type(tmp_path):
    """Test filtering files by type"""
    core_root = tmp_path / "core"
    core_root.mkdir()
    
    converter = FilesetConverter(core_root)
    
    files = [
        {'path': 'test.v', 'type': 'verilog', 'name': 'test.v'},
        {'path': 'test.sv', 'type': 'systemverilog', 'name': 'test.sv'},
        {'path': 'test.xdc', 'type': 'constraint', 'name': 'test.xdc'},
    ]
    
    verilog_files = converter.filter_by_type(files, ['verilog'])
    source_files = converter.get_source_files(files)
    
    assert len(verilog_files) == 1
    assert verilog_files[0]['type'] == 'verilog'
    
    assert len(source_files) == 2
    assert all(f['type'] in ['verilog', 'systemverilog', 'vhdl'] for f in source_files)


def test_files_root_separation(tmp_path):
    """Test handling when files_root differs from core_root"""
    core_root = tmp_path / "core"
    files_root = tmp_path / "files"
    
    core_root.mkdir()
    files_root.mkdir()
    
    # File in files_root (e.g., fetched dependency)
    (files_root / "fetched.v").write_text("module fetched; endmodule")
    
    converter = FilesetConverter(core_root, files_root)
    
    fusesoc_files = [
        {'name': 'fetched.v', 'file_type': 'verilogSource'},
    ]
    
    converted = converter.convert_files(fusesoc_files)
    
    assert len(converted) == 1
    assert Path(converted[0]['path']).exists()
    assert 'fetched.v' in converted[0]['path']
