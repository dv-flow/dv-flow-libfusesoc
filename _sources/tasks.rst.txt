======================
DV Flow Task Reference
======================

This section documents the DV Flow tasks provided by libfusesoc.

Task Overview
=============

libfusesoc provides tasks organized into packages:

* **fusesoc** - Core management tasks
* **fusesoc.edalize.sim** - Simulation flow tasks
* **fusesoc.edalize.fpga** - FPGA synthesis tasks (stub)
* **fusesoc.edalize.lint** - Linting tasks (stub)

fusesoc Package
===============

CoreResolve Task
----------------

.. code-block:: text

   Task: fusesoc.CoreResolve
   Description: Resolve FuseSoC core and retrieve file lists

**Purpose:**
Resolves a FuseSoC core by VLNV identifier, extracts all files, dependencies, 
and metadata. This is typically the first step in any flow using FuseSoC cores.

**Input Parameters:**

:core: Core VLNV (vendor:library:name:version)
:target: Target configuration (default: "sim")
:tool: Tool name for tool-specific filesets (optional)
:libraries: Additional library mappings (dict)
:workspace: FuseSoC workspace directory path
:flags: Build flags (list)

**Output Values:**

:core_name: Resolved core name
:core_root: Core root directory path
:files: Converted file list (list of dicts)
:dependencies: Core dependencies (list)
:parameters: Core parameters (dict)
:include_dirs: Include directory paths (list)

**Example Usage:**

.. code-block:: python

   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams

   # Resolve a UART core for simulation
   result = await CoreResolve(runner, CoreResolveParams(
       core="vendor:lib:uart:1.0",
       target="sim",
       tool="icarus",
       workspace="/tmp/fusesoc_workspace",
       libraries={
           "mylib": "/path/to/custom/cores"
       }
   ))

   # Access outputs
   print(f"Resolved: {result.output['core_name']}")
   print(f"Found {len(result.output['files'])} files")
   for file in result.output['files']:
       print(f"  {file['name']} ({file['file_type']})")

**Caching:**
The task supports memento-based caching. Results are cached based on the input 
parameters, avoiding redundant core resolution.

CoreFetch Task
--------------

.. code-block:: text

   Task: fusesoc.CoreFetch
   Description: Fetch remote FuseSoC core dependencies

**Status:** Not yet implemented

**Purpose:**
Fetches remote FuseSoC cores from git repositories or other sources into the 
local workspace.

fusesoc.edalize.sim Package
===========================

The simulation package provides three tasks that form a complete simulation pipeline.

SimConfigure Task
-----------------

.. code-block:: text

   Task: fusesoc.edalize.sim.SimConfigure
   Description: Configure simulation using Edalize

**Purpose:**
Configures a simulation tool with the design files and parameters. Builds the EDAM 
structure and sets up the Edalize backend.

**Input Parameters:**

:core_name: Name of the design
:files: File list from CoreResolve
:include_dirs: Include directory paths (list)
:toplevel: Toplevel module name
:tool: Simulation tool (icarus, verilator, modelsim, vcs, xcelium, ghdl)
:parameters: Build-time parameters (dict)
:plusargs: Runtime plusargs (list)
:tool_options: Tool-specific options (dict)

**Output Values:**

:work_root: Edalize work directory path
:tool: Configured simulation tool name
:configured: Configuration success flag (bool)

**Supported Tools:**

* **icarus** - Icarus Verilog (open-source)
* **verilator** - Verilator (open-source, high-performance)
* **modelsim** - ModelSim/Questa (commercial)
* **vcs** - Synopsys VCS (commercial)
* **xcelium** - Cadence Xcelium (commercial)
* **ghdl** - GHDL VHDL simulator (open-source)

**Example Usage:**

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import SimConfigure, SimConfigureParams

   result = await SimConfigure(runner, SimConfigureParams(
       core_name="my_uart",
       files=core_result.output['files'],
       include_dirs=core_result.output['include_dirs'],
       toplevel="uart_tb",
       tool="icarus",
       parameters={
           'BAUD_RATE': 115200,
           'DATA_WIDTH': 8
       },
       plusargs=['+dump_waves'],
       tool_options={
           'icarus': {
               'iverilog_options': ['-g2009']
           }
       }
   ))

SimBuild Task
-------------

.. code-block:: text

   Task: fusesoc.edalize.sim.SimBuild
   Description: Build simulation executable/model
   Dependencies: SimConfigure

**Purpose:**
Compiles and elaborates the design to produce a simulation executable or model.

**Input Parameters:**

:work_root: Edalize work directory (from SimConfigure)
:tool: Simulation tool name

**Output Values:**

:work_root: Edalize work directory path
:build_success: Build success status (bool)
:executable: Path to simulation executable

**Example Usage:**

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import SimBuild, SimBuildParams

   result = await SimBuild(runner, SimBuildParams(
       work_root=config_result.output['work_root'],
       tool=config_result.output['tool']
   ))

   if result.output['build_success']:
       print(f"Build succeeded: {result.output['executable']}")
   else:
       print("Build failed!")

**Error Handling:**
If compilation fails, the task marks the build as unsuccessful. Check the 
``build_success`` output and examine logs in the work_root directory.

SimRun Task
-----------

.. code-block:: text

   Task: fusesoc.edalize.sim.SimRun
   Description: Execute simulation with runtime parameters
   Dependencies: SimBuild

**Purpose:**
Executes the compiled simulation with runtime arguments and captures results.

**Input Parameters:**

:work_root: Edalize work directory (from SimBuild)
:tool: Simulation tool name
:runtime_plusargs: Additional runtime plusargs (list)

**Output Values:**

:work_root: Edalize work directory path
:run_success: Simulation success status (bool)
:log_file: Path to simulation log file

**Example Usage:**

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import SimRun, SimRunParams

   result = await SimRun(runner, SimRunParams(
       work_root=build_result.output['work_root'],
       tool=build_result.output['tool'],
       runtime_plusargs=[
           '+testname=basic_test',
           '+seed=12345'
       ]
   ))

   if result.output['run_success']:
       print("Simulation PASSED")
   else:
       print("Simulation FAILED")
   
   # Read simulation log
   with open(result.output['log_file']) as f:
       print(f.read())

**Success Detection:**
The task attempts to determine success/failure based on:

* Tool exit code
* Presence of error messages in output
* Tool-specific success indicators

Complete Simulation Flow Example
---------------------------------

Putting it all together:

.. code-block:: python

   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams
   from dv_flow.libfusesoc.edalize_sim import (
       SimConfigure, SimConfigureParams,
       SimBuild, SimBuildParams,
       SimRun, SimRunParams
   )

   # Step 1: Resolve the core
   print("Resolving core...")
   core = await CoreResolve(runner, CoreResolveParams(
       core="my_vendor:lib:my_ip:1.0",
       target="sim",
       workspace="/tmp/fusesoc_ws"
   ))

   # Step 2: Configure simulation
   print("Configuring simulation...")
   config = await SimConfigure(runner, SimConfigureParams(
       core_name=core.output['core_name'],
       files=core.output['files'],
       include_dirs=core.output['include_dirs'],
       toplevel="top_tb",
       tool="verilator",
       parameters={'CLK_FREQ': 100_000_000}
   ))

   # Step 3: Build
   print("Building simulation...")
   build = await SimBuild(runner, SimBuildParams(
       work_root=config.output['work_root'],
       tool=config.output['tool']
   ))

   if not build.output['build_success']:
       print("Build failed!")
       exit(1)

   # Step 4: Run
   print("Running simulation...")
   run = await SimRun(runner, SimRunParams(
       work_root=build.output['work_root'],
       tool=build.output['tool'],
       runtime_plusargs=['+verbose=2']
   ))

   # Check results
   if run.output['run_success']:
       print("✅ Test PASSED")
   else:
       print("❌ Test FAILED")
       print(f"See log: {run.output['log_file']}")

fusesoc.edalize.fpga Package
============================

.. note::
   FPGA flow tasks are currently stubs and not yet implemented.

**Planned Tasks:**

* **FPGAConfigure** - Configure FPGA synthesis flow
* **FPGABuild** - Run synthesis and place & route
* **FPGAProgram** - Program FPGA device

fusesoc.edalize.lint Package
=============================

.. note::
   Linting flow tasks are currently stubs and not yet implemented.

**Planned Tasks:**

* **LintConfigure** - Configure linting tool
* **LintRun** - Execute lint checks

Task Development Guide
======================

Creating Custom Tasks
---------------------

To create custom tasks that integrate with libfusesoc:

1. Import the CoreResolve task to get FuseSoC core files
2. Use the file lists and parameters in your custom task
3. Follow DV Flow task patterns (Pydantic models, async/await)

Example custom task:

.. code-block:: python

   from pydantic import BaseModel
   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams

   class MyCustomParams(BaseModel):
       core: str
       workspace: str
       # ... custom parameters

   class MyCustomOutput(BaseModel):
       success: bool
       # ... custom outputs

   class MyCustomTask:
       async def __call__(self, runner, params: MyCustomParams):
           # First, resolve the core
           core_result = await CoreResolve(runner, CoreResolveParams(
               core=params.core,
               workspace=params.workspace
           ))
           
           # Now use the files in your custom logic
           files = core_result.output['files']
           
           # ... your custom task logic ...
           
           return MyCustomOutput(success=True)

Best Practices
--------------

1. **Always resolve cores first**: Use CoreResolve before other operations
2. **Chain tasks properly**: Pass outputs to next task's inputs
3. **Handle errors gracefully**: Check success flags and provide diagnostics
4. **Use appropriate tools**: Choose the right simulator/synthesizer for your needs
5. **Leverage caching**: CoreResolve caches results automatically
6. **Isolate workspaces**: Use separate workspace directories for different projects
