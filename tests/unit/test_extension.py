#****************************************************************************
#* test_extension.py
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
from dv_flow.libfusesoc.__ext__ import dvfm_packages


def test_dvfm_packages_registration():
    """Test that dvfm_packages returns correct package definitions"""
    packages = dvfm_packages()
    
    # Verify expected packages are registered
    assert 'fusesoc' in packages
    assert 'fusesoc.edalize.sim' in packages
    assert 'fusesoc.edalize.fpga' in packages
    assert 'fusesoc.edalize.lint' in packages
    
    # Verify all paths point to .dv files
    for name, path in packages.items():
        assert path.endswith('.dv'), f"Package {name} should point to .dv file"
        assert os.path.exists(path), f"Flow file {path} for {name} should exist"


def test_flow_files_exist():
    """Test that all registered flow definition files exist"""
    packages = dvfm_packages()
    
    for name, path in packages.items():
        file_path = Path(path)
        assert file_path.exists(), f"Flow file for {name} does not exist: {path}"
        assert file_path.is_file(), f"Flow path for {name} is not a file: {path}"
        
        # Verify it's readable
        content = file_path.read_text()
        assert len(content) > 0, f"Flow file for {name} is empty: {path}"
        assert 'package:' in content, f"Flow file for {name} should contain 'package:' section"
