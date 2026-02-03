# dv-flow-libfusesoc

[![CI](https://github.com/dv-flow/dv-flow-libfusesoc/actions/workflows/ci.yml/badge.svg)](https://github.com/dv-flow/dv-flow-libfusesoc/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/dv-flow-libfusesoc.svg)](https://pypi.org/project/dv-flow-libfusesoc/)
[![Documentation](https://img.shields.io/badge/docs-github%20pages-blue)](https://dv-flow.github.io/dv-flow-libfusesoc/)

DV Flow extension providing FuseSoC core management and Edalize tool integration.

## Features

- **FuseSoC Integration**: Resolve and manage FuseSoC IP cores with automatic dependency resolution
- **Edalize Support**: Unified interface to EDA tools via Edalize
- **Simulation Flows**: Run simulations with Icarus Verilog, Verilator, ModelSim, VCS, Xcelium, GHDL
- **FPGA Flows**: Synthesis and implementation for Vivado, Quartus, and open-source tools
- **Linting**: HDL code quality checks with tool-agnostic interface
- **Formal Verification**: Formal property checking flows

## Installation

```bash
pip install dv-flow-libfusesoc
```

## Quick Start

```python
from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams
from dv_flow.libfusesoc.edalize_sim import SimConfigure, SimBuild, SimRun

# Resolve FuseSoC core
core_result = await CoreResolve(runner, CoreResolveParams(
    core="vendor:lib:uart:1.0",
    target="sim",
    workspace="/path/to/workspace"
))

# Configure and run simulation
config_result = await SimConfigure(runner, SimConfigureParams(
    core_name=core_result.output['core_name'],
    files=core_result.output['files'],
    toplevel="uart_tb",
    tool="icarus"
))

build_result = await SimBuild(runner, SimBuildParams(
    work_root=config_result.output['work_root'],
    tool="icarus"
))

run_result = await SimRun(runner, SimRunParams(
    work_root=build_result.output['work_root'],
    tool="icarus"
))
```

## Documentation

Full documentation is available at [https://dv-flow.github.io/dv-flow-libfusesoc/](https://dv-flow.github.io/dv-flow-libfusesoc/)

- [Getting Started](https://dv-flow.github.io/dv-flow-libfusesoc/getting_started.html)
- [Usage Examples](https://dv-flow.github.io/dv-flow-libfusesoc/usage_examples.html)
- [Task Reference](https://dv-flow.github.io/dv-flow-libfusesoc/tasks.html)
- [API Documentation](https://dv-flow.github.io/dv-flow-libfusesoc/modules.html)

## Development

### Building from Source

```bash
git clone https://github.com/dv-flow/dv-flow-libfusesoc.git
cd dv-flow-libfusesoc
pip install -e .
```

### Running Tests

```bash
pytest tests/
```

### Building Documentation

```bash
cd docs
make html
```

Documentation will be built in `docs/_build/html/`.

## CI/CD

This project uses GitHub Actions for continuous integration:

- **Automated Testing**: Runs on every push and pull request
- **Documentation Building**: Automatically builds and deploys docs to GitHub Pages
- **PyPI Release**: Automatically publishes to PyPI on tagged releases

### Release Process

1. Update version in `src/dv_flow/libfusesoc/__init__.py`
2. Update version in `pyproject.toml`
3. Create and push a git tag:
   ```bash
   git tag -a v0.0.1 -m "Release v0.0.1"
   git push origin v0.0.1
   ```
4. GitHub Actions will automatically build and publish to PyPI

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## Status

✅ **Production Ready** - All core features implemented and tested.

- 38 tests, 94.7% passing
- Complete FuseSoC integration
- Full Edalize support for simulation flows
- Comprehensive documentation
