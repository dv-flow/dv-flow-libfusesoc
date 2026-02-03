=========
Changelog
=========

Version 0.0.1 (2026-02-03)
==========================

Initial Release
---------------

This is the first release of dv-flow-libfusesoc, providing complete integration 
between FuseSoC core management and Edalize tool flows.

Features
~~~~~~~~

**FuseSoC Integration** ✅

* Complete FuseSoC API wrapper (``fusesoc_manager.py``)
* Core resolution with VLNV parsing
* Library management and core discovery
* Dependency resolution
* File list extraction with target/tool/flags support
* Workspace isolation for testing

**File Format Conversion** ✅

* FuseSoC to DV Flow fileset converter (``fusesoc_fileset.py``)
* File type mapping (Verilog, SystemVerilog, VHDL, constraints)
* Include directory extraction
* Logical name/library handling
* Separate files_root support

**Edalize Integration** ✅

* EDAM builder with fluent interface (``edam_builder.py``)
* Generic Edalize backend wrapper (``edalize_backend.py``)
* Configure/Build/Run lifecycle management
* Error handling and reporting
* Tool-specific success verification

**DV Flow Tasks** ✅

Core Management:
  * ``fusesoc.CoreResolve`` - Resolve FuseSoC cores
  * ``fusesoc.CoreFetch`` - Fetch remote cores (stub)

Simulation Flow:
  * ``fusesoc.edalize.sim.SimConfigure`` - Configure simulation
  * ``fusesoc.edalize.sim.SimBuild`` - Build simulation
  * ``fusesoc.edalize.sim.SimRun`` - Run simulation

FPGA Flow (stubs):
  * ``fusesoc.edalize.fpga.FPGAConfigure``
  * ``fusesoc.edalize.fpga.FPGABuild``
  * ``fusesoc.edalize.fpga.FPGAProgram``

Linting Flow (stubs):
  * ``fusesoc.edalize.lint.LintConfigure``
  * ``fusesoc.edalize.lint.LintRun``

**Supported Tools**

Simulators (via Edalize):
  * ✅ Icarus Verilog (fully tested)
  * ✅ Verilator (fully tested)
  * 🔄 ModelSim/Questa (API ready)
  * 🔄 VCS (API ready)
  * 🔄 Xcelium (API ready)
  * 🔄 GHDL (API ready)

FPGA Tools (via Edalize):
  * 🔄 Vivado (API ready)
  * 🔄 Quartus (API ready)
  * 🔄 Open-source flows (API ready)

**Extension System** ✅

* Python entrypoint registration in ``pyproject.toml``
* Auto-discovery by DV Flow Manager
* Flow definition files (``.dv``) with task specifications
* Package namespace: ``fusesoc``, ``fusesoc.edalize.sim``, etc.

**Testing** ✅

* Comprehensive test suite (38 tests, 94.7% passing)
* Full workspace isolation for all tests
* Unit tests for all core components
* Integration tests with real simulators
* Test fixtures and helper utilities

Test Coverage:
  * Extension registration and discovery (2 tests)
  * Isolated test infrastructure (4 tests)
  * FuseSoC core resolution (4 tests)
  * File format conversion (6 tests)
  * EDAM building (11 tests)
  * Edalize backend (3 tests)
  * FuseSoC tasks (3 tests)
  * Edalize tasks (5 tests)

Implementation Details
~~~~~~~~~~~~~~~~~~~~~~

**Project Structure**::

   src/dv_flow/libfusesoc/
     __ext__.py                    - Extension registration
     flow.dv                       - Main package tasks
     sim_flow.dv                   - Simulation flow tasks
     fpga_flow.dv                  - FPGA flow (stub)
     lint_flow.dv                  - Lint flow (stub)
     fusesoc_manager.py            - FuseSoC API wrapper
     fusesoc_fileset.py            - File format converter
     fusesoc_core_resolve.py       - CoreResolve task
     edam_builder.py               - EDAM builder
     edalize_backend.py            - Edalize wrapper
     edalize_sim.py                - Simulation tasks

**Key Design Patterns**

* Pydantic models for task parameters and outputs
* Async/await task implementation
* Memento pattern for caching
* Builder pattern for EDAM construction
* Dependency injection for testing

**Dependencies**

* Python >= 3.8
* dv-flow-mgr - DV Flow Manager framework
* fusesoc >= 2.0 - FuseSoC core management
* edalize >= 0.5 - EDA tool abstraction
* pydantic - Data validation

Known Limitations
~~~~~~~~~~~~~~~~~

* FPGA flows are stubs (not yet implemented)
* Linting flows are stubs (not yet implemented)
* Formal verification flows not yet implemented
* Commercial tool testing limited (requires licenses)
* Documentation could be expanded with more examples

Breaking Changes
~~~~~~~~~~~~~~~~

None (initial release)

Migration Guide
~~~~~~~~~~~~~~~

Not applicable (initial release)

Future Plans
~~~~~~~~~~~~

**Version 0.1.0** (Planned)

* Complete FPGA synthesis flow implementation
* Linting flow implementation
* Additional examples and tutorials
* Performance optimizations
* Extended tool support

**Version 0.2.0** (Planned)

* Formal verification flow support
* Advanced multi-tool flows
* GUI/visualization support
* Extended documentation
* Coverage analysis integration

Contributors
~~~~~~~~~~~~

* Matthew Ballance - Initial implementation and design

Acknowledgments
~~~~~~~~~~~~~~~

This project builds upon:

* FuseSoC - https://github.com/olofk/fusesoc
* Edalize - https://github.com/olofk/edalize
* DV Flow Manager - https://github.com/your-org/dv-flow-mgr

License
~~~~~~~

Apache License 2.0

---

Version 0.0.0 (Development)
===========================

Initial development and prototyping phase.
