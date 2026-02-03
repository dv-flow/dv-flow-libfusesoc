===============
Quick Reference
===============

Common Commands
===============

Core Resolution
---------------

.. code-block:: python

   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams
   
   result = await CoreResolve(runner, CoreResolveParams(
       core="vendor:lib:name:version",
       target="sim",
       workspace="/path/to/workspace"
   ))

Simulation Flow
---------------

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import (
       SimConfigure, SimConfigureParams,
       SimBuild, SimBuildParams,
       SimRun, SimRunParams
   )
   
   # Configure
   config = await SimConfigure(runner, SimConfigureParams(
       core_name="my_core",
       files=files,
       toplevel="top_tb",
       tool="icarus"
   ))
   
   # Build
   build = await SimBuild(runner, SimBuildParams(
       work_root=config.output['work_root'],
       tool="icarus"
   ))
   
   # Run
   run = await SimRun(runner, SimRunParams(
       work_root=build.output['work_root'],
       tool="icarus"
   ))

Parameter Reference
===================

CoreResolve Parameters
----------------------

========== ======== ========================================
Parameter  Type     Description
========== ======== ========================================
core       str      VLNV identifier (required)
target     str      Target configuration (default: "sim")
tool       str      Tool name (optional)
libraries  dict     Additional libraries {name: path}
workspace  str      FuseSoC workspace path (required)
flags      list     Build flags (optional)
========== ======== ========================================

SimConfigure Parameters
-----------------------

============= ======== ========================================
Parameter     Type     Description
============= ======== ========================================
core_name     str      Design name (required)
files         list     File list (required)
include_dirs  list     Include directories
toplevel      str      Top module name (required)
tool          str      Simulator tool (required)
parameters    dict     Build-time parameters
plusargs      list     Runtime plusargs
tool_options  dict     Tool-specific options
============= ======== ========================================

Supported Tools
===============

Simulators
----------

========== ============== =================
Tool       Type           Status
========== ============== =================
icarus     Open-source    ✅ Fully supported
verilator  Open-source    ✅ Fully supported
modelsim   Commercial     🔄 API ready
vcs        Commercial     🔄 API ready
xcelium    Commercial     🔄 API ready
ghdl       Open-source    🔄 API ready
========== ============== =================

Tool-Specific Options
=====================

Icarus Verilog
--------------

.. code-block:: python

   tool_options = {
       'icarus': {
           'iverilog_options': ['-g2009', '-Wall'],
           'timescale': '1ns/1ps'
       }
   }

Verilator
---------

.. code-block:: python

   tool_options = {
       'verilator': {
           'verilator_options': [
               '--trace',
               '--trace-depth 2',
               '-O3',
               '-Wall'
           ],
           'make_options': ['-j4']
       }
   }

ModelSim/Questa
---------------

.. code-block:: python

   tool_options = {
       'modelsim': {
           'vlog_options': ['-sv'],
           'vsim_options': ['-voptargs=+acc']
       }
   }

VCS
---

.. code-block:: python

   tool_options = {
       'vcs': {
           'vcs_options': ['-sverilog', '-full64'],
           'run_options': []
       }
   }

Common Patterns
===============

Pattern: Multiple Test Cases
-----------------------------

.. code-block:: python

   tests = ['test1', 'test2', 'test3']
   
   for test in tests:
       config = await SimConfigure(...)
       build = await SimBuild(...)
       run = await SimRun(runner, SimRunParams(
           work_root=build.output['work_root'],
           tool="icarus",
           runtime_plusargs=[f"+testname={test}"]
       ))

Pattern: Parameterized Configurations
--------------------------------------

.. code-block:: python

   configs = [
       {'WIDTH': 8, 'DEPTH': 16},
       {'WIDTH': 16, 'DEPTH': 32},
   ]
   
   for params in configs:
       config = await SimConfigure(runner, SimConfigureParams(
           # ... other params ...
           parameters=params
       ))

Pattern: Error Handling
------------------------

.. code-block:: python

   try:
       core = await CoreResolve(runner, params)
   except Exception as e:
       print(f"Resolution failed: {e}")
       return
   
   build = await SimBuild(runner, build_params)
   if not build.output['build_success']:
       print("Build failed!")
       return

File Type Mappings
==================

FuseSoC to DV Flow
------------------

======================= ===================
FuseSoC Type            DV Flow Type
======================= ===================
verilogSource           verilog
systemVerilogSource     systemverilog
vhdlSource              vhdl
tclSource               tcl
SDC                     sdc
xdc                     xdc
user                    user
======================= ===================

Environment Variables
=====================

FuseSoC Variables
-----------------

==================== ========================================
Variable             Description
==================== ========================================
XDG_DATA_HOME        FuseSoC data directory
XDG_CONFIG_HOME      FuseSoC config directory
FUSESOC_CORES_ROOT   Core library search paths
==================== ========================================

Troubleshooting
===============

Common Errors
-------------

**Core not found**
   - Check VLNV spelling
   - Verify workspace path
   - Ensure .core file exists

**Build failed**
   - Check compiler installation
   - Verify file paths
   - Review syntax errors

**Tool not found**
   - Check PATH environment
   - Verify tool installation
   - Use ``which <tool>`` to locate

Debug Commands
--------------

.. code-block:: bash

   # Check FuseSoC installation
   fusesoc --version
   
   # List available cores
   fusesoc core list
   
   # Check simulator
   iverilog -v
   verilator --version
   
   # Verify Python package
   python -c "import dv_flow.libfusesoc; print('OK')"

Performance Tips
================

* Use Verilator for large designs (10-100x faster)
* Enable optimization flags (``-O3`` for Verilator)
* Cache core resolution results
* Use incremental builds when possible
* Run tests in parallel with ``asyncio.gather()``

Additional Resources
====================

* :doc:`getting_started` - Detailed tutorial
* :doc:`usage_examples` - More examples
* :doc:`tasks` - Complete task reference
* :doc:`fusesoc_integration` - FuseSoC API
* :doc:`edalize_integration` - Edalize API

External Links
--------------

* `FuseSoC Documentation <https://fusesoc.readthedocs.io/>`_
* `Edalize Documentation <https://edalize.readthedocs.io/>`_
* `Icarus Verilog <http://iverilog.icarus.com/>`_
* `Verilator <https://www.veripool.org/verilator/>`_
