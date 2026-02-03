import os
import pytest
import shutil
from pathlib import Path
from typing import Dict


class IsolatedFuseSoCWorkspace:
    """Context manager for isolated FuseSoC workspace"""
    
    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path
        self.workspace = tmp_path / "fusesoc_workspace"
        self.config_dir = tmp_path / "config"
        self.data_dir = tmp_path / "data"
        self.cache_dir = tmp_path / "cache"
        self.old_env = {}
        
    def __enter__(self):
        # Create directories
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Save and override environment variables
        env_vars = [
            'XDG_DATA_HOME',
            'XDG_CONFIG_HOME',
            'XDG_CACHE_HOME',
            'FUSESOC_CORES_ROOT',
        ]
        
        for var in env_vars:
            self.old_env[var] = os.environ.get(var)
        
        # Set isolated environment
        os.environ['XDG_DATA_HOME'] = str(self.data_dir)
        os.environ['XDG_CONFIG_HOME'] = str(self.config_dir)
        os.environ['XDG_CACHE_HOME'] = str(self.cache_dir)
        os.environ['FUSESOC_CORES_ROOT'] = str(self.workspace)
        
        # Create minimal FuseSoC config
        fusesoc_conf_dir = self.config_dir / "fusesoc"
        fusesoc_conf_dir.mkdir(parents=True, exist_ok=True)
        fusesoc_conf = fusesoc_conf_dir / "fusesoc.conf"
        fusesoc_conf.write_text("[main]\ncache_root = {}\n".format(self.cache_dir))
        
        return self
        
    def __exit__(self, *args):
        # Restore old environment
        for var, value in self.old_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value
        
        # Cleanup is handled by tmp_path fixture
        
    def add_test_core(self, core_file: Path, sources: list = None):
        """Add a test .core file to workspace with optional source files"""
        # Copy core file
        dest_core = self.workspace / core_file.name
        shutil.copy(core_file, dest_core)
        
        # Copy source files if provided
        if sources:
            for src in sources:
                src_path = Path(src)
                dest_src = self.workspace / src_path.name
                shutil.copy(src_path, dest_src)
                
        return dest_core
        
    def add_library(self, name: str, path: Path):
        """Add a library to isolated FuseSoC configuration"""
        # This would integrate with FuseSoC's library management
        # Implementation depends on FuseSoC API
        pass
        
    def get_core_root(self) -> Path:
        """Get the workspace root directory"""
        return self.workspace


@pytest.fixture
def isolated_fusesoc_workspace(tmp_path):
    """
    Create isolated FuseSoC workspace in tmp_path.
    Sets environment variables to isolate from user installation.
    Returns IsolatedFuseSoCWorkspace instance.
    """
    with IsolatedFuseSoCWorkspace(tmp_path) as workspace:
        yield workspace


@pytest.fixture
def isolated_edalize_workspace(tmp_path):
    """
    Create isolated Edalize build directory.
    Ensures all tool outputs go to test directory.
    """
    build_dir = tmp_path / "edalize_build"
    build_dir.mkdir(parents=True, exist_ok=True)
    return build_dir


@pytest.fixture
def test_cores_dir():
    """Return path to test cores directory"""
    tests_dir = Path(__file__).parent
    return tests_dir / "fixtures" / "test_cores"
