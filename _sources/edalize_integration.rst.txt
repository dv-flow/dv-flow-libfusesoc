====================
Edalize Integration
====================

This module provides integration with Edalize for EDA tool flows.

edam_builder
============

.. automodule:: dv_flow.libfusesoc.edam_builder
   :members:
   :undoc-members:
   :show-inheritance:

The EDAM Builder constructs Edalize Design Abstraction Model (EDAM) structures.

EDAM Structure
--------------

EDAM is Edalize's unified data structure for describing designs:

.. code-block:: python

   edam = {
       'name': 'design_name',
       'files': [
           {'name': 'file.v', 'file_type': 'verilogSource'},
           {'name': 'file.sv', 'file_type': 'systemVerilogSource'},
       ],
       'toplevel': 'top_module',
       'parameters': {
           'WIDTH': 32,
           'DEPTH': 1024
       },
       'tool_options': {
           'icarus': {
               'iverilog_options': ['-g2009']
           }
       }
   }

Builder Pattern
---------------

The EdamBuilder uses a fluent interface for constructing EDAM:

.. code-block:: python

   from dv_flow.libfusesoc.edam_builder import EdamBuilder

   builder = EdamBuilder("my_design")
   builder.set_toplevel("top_module")
   builder.add_files(file_list)
   builder.add_parameters({'WIDTH': 32})
   builder.add_include_dirs(['/path/to/includes'])
   builder.set_tool_options('icarus', {'iverilog_options': ['-g2009']})
   
   edam = builder.build()

Convenience Functions
---------------------

**build_edam_from_core()**
   Builds EDAM directly from CoreResolve output:

.. code-block:: python

   from dv_flow.libfusesoc.edam_builder import build_edam_from_core

   edam = build_edam_from_core(
       core_name="uart",
       files=core_result.output['files'],
       toplevel="uart_top",
       tool="icarus",
       parameters={'BAUD_RATE': 115200}
   )

edalize_backend
===============

.. automodule:: dv_flow.libfusesoc.edalize_backend
   :members:
   :undoc-members:
   :show-inheritance:

The Edalize Backend provides a wrapper around Edalize tool flows.

Backend Lifecycle
-----------------

The backend manages the three-phase Edalize lifecycle:

1. **Configure**: Setup tool environment and generate build scripts
2. **Build**: Compile/elaborate the design
3. **Run**: Execute the tool (simulation, synthesis, etc.)

.. code-block:: python

   from dv_flow.libfusesoc.edalize_backend import EdalizeBackend

   backend = EdalizeBackend(edam, work_root, tool="icarus")
   
   # Phase 1: Configure
   backend.configure()
   
   # Phase 2: Build
   success = backend.build()
   if not success:
       print("Build failed!")
       print(backend.get_stderr())
   
   # Phase 3: Run
   success = backend.run()

Error Handling
--------------

The backend provides comprehensive error reporting:

* ``get_stdout()`` - Capture tool standard output
* ``get_stderr()`` - Capture tool standard error  
* ``get_returncode()`` - Get tool exit code
* Tool-specific success verification

Convenience Functions
---------------------

**create_sim_backend()**
   Creates a backend configured for simulation:

.. code-block:: python

   from dv_flow.libfusesoc.edalize_backend import create_sim_backend

   backend = create_sim_backend(
       edam=edam,
       work_root="/path/to/work",
       tool="verilator"
   )

**create_fpga_backend()**
   Creates a backend configured for FPGA synthesis:

.. code-block:: python

   from dv_flow.libfusesoc.edalize_backend import create_fpga_backend

   backend = create_fpga_backend(
       edam=edam,
       work_root="/path/to/work",
       tool="vivado"
   )

edalize_sim
===========

.. automodule:: dv_flow.libfusesoc.edalize_sim
   :members:
   :undoc-members:
   :show-inheritance:

Simulation tasks for running HDL simulations through Edalize.

SimConfigure Task
-----------------

Configures a simulation environment.

**Parameters:**

.. code-block:: python

   class SimConfigureParams(BaseModel):
       core_name: str
       files: List[Dict]
       include_dirs: List[str] = []
       toplevel: str
       tool: str = "icarus"
       parameters: Dict[str, Any] = {}
       plusargs: List[str] = []
       tool_options: Dict[str, Any] = {}

**Outputs:**

.. code-block:: python

   class SimConfigureOutput(BaseModel):
       work_root: str
       tool: str
       configured: bool

**Example:**

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import SimConfigure, SimConfigureParams

   result = await SimConfigure(runner, SimConfigureParams(
       core_name="uart",
       files=file_list,
       toplevel="uart_tb",
       tool="icarus",
       parameters={'BAUD_RATE': 115200}
   ))

SimBuild Task
-------------

Builds the simulation executable.

**Parameters:**

.. code-block:: python

   class SimBuildParams(BaseModel):
       work_root: str
       tool: str

**Outputs:**

.. code-block:: python

   class SimBuildOutput(BaseModel):
       work_root: str
       build_success: bool
       executable: str

**Example:**

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import SimBuild, SimBuildParams

   result = await SimBuild(runner, SimBuildParams(
       work_root=config_result.output['work_root'],
       tool="icarus"
   ))

SimRun Task
-----------

Executes the simulation.

**Parameters:**

.. code-block:: python

   class SimRunParams(BaseModel):
       work_root: str
       tool: str
       runtime_plusargs: List[str] = []

**Outputs:**

.. code-block:: python

   class SimRunOutput(BaseModel):
       work_root: str
       run_success: bool
       log_file: str

**Example:**

.. code-block:: python

   from dv_flow.libfusesoc.edalize_sim import SimRun, SimRunParams

   result = await SimRun(runner, SimRunParams(
       work_root=build_result.output['work_root'],
       tool="icarus",
       runtime_plusargs=['+verbose=1']
   ))

Task Chaining
-------------

The simulation tasks are designed to be chained together:

.. code-block:: python

   # Complete simulation flow
   config = await SimConfigure(runner, config_params)
   
   build = await SimBuild(runner, SimBuildParams(
       work_root=config.output['work_root'],
       tool=config.output['tool']
   ))
   
   run = await SimRun(runner, SimRunParams(
       work_root=build.output['work_root'],
       tool=build.output['tool']
   ))
   
   if run.output['run_success']:
       print("Simulation passed!")
       print(f"Log: {run.output['log_file']}")
