====================
FuseSoC Integration
====================

This module provides integration with FuseSoC for IP core management.

fusesoc_manager
===============

.. automodule:: dv_flow.libfusesoc.fusesoc_manager
   :members:
   :undoc-members:
   :show-inheritance:

The FuseSoC Manager provides a wrapper around FuseSoC's core functionality, enabling:

* Core discovery and resolution
* Library management
* Dependency tracking
* File list extraction
* Workspace isolation

Key Features
------------

**Core Resolution**
   Parse VLNV (Vendor:Library:Name:Version) identifiers and resolve cores with their dependencies.

**Library Management**
   Add and manage FuseSoC libraries, with support for multiple core sources.

**File Extraction**
   Extract file lists filtered by target, tool, and flags.

**Workspace Isolation**
   All operations are performed within a configured workspace directory, 
   ensuring no interference with user's global FuseSoC configuration.

fusesoc_fileset
===============

.. automodule:: dv_flow.libfusesoc.fusesoc_fileset
   :members:
   :undoc-members:
   :show-inheritance:

The Fileset Converter transforms FuseSoC file structures into DV Flow compatible formats.

Conversion Features
-------------------

* Maps FuseSoC file types to standard categories (Verilog, SystemVerilog, VHDL, constraints)
* Extracts include directories
* Handles logical names and library specifications
* Supports separate files_root for file path resolution
* Preserves file metadata and attributes

File Type Mapping
-----------------

======================= ====================
FuseSoC                 DV Flow
======================= ====================
verilogSource           verilog
systemVerilogSource     systemverilog
vhdlSource              vhdl
tclSource               tcl
SDC                     sdc
xdc                     xdc
user                    user
======================= ====================

fusesoc_core_resolve
====================

.. automodule:: dv_flow.libfusesoc.fusesoc_core_resolve
   :members:
   :undoc-members:
   :show-inheritance:

The CoreResolve task is the main entry point for resolving FuseSoC cores in DV Flow.

Task Parameters
---------------

The task accepts the following parameters through ``CoreResolveParams``:

.. code-block:: python

   class CoreResolveParams(BaseModel):
       core: str  # VLNV identifier
       target: str = "sim"  # Target configuration
       tool: Optional[str] = None  # Tool name
       libraries: Dict[str, str] = {}  # Additional libraries
       workspace: str  # FuseSoC workspace path
       flags: List[str] = []  # Build flags

Task Outputs
------------

Returns ``CoreResolveOutput`` containing:

.. code-block:: python

   class CoreResolveOutput(BaseModel):
       core_name: str  # Resolved core name
       core_root: str  # Core root directory
       files: List[Dict]  # Converted file list
       dependencies: List[str]  # Core dependencies
       parameters: Dict[str, Any]  # Core parameters
       include_dirs: List[str]  # Include directories

Usage Example
-------------

.. code-block:: python

   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams

   params = CoreResolveParams(
       core="vendor:lib:uart:1.0",
       target="sim",
       workspace="/path/to/workspace",
       libraries={"mylib": "/path/to/mylib"}
   )

   result = await CoreResolve(runner, params)
   
   print(f"Resolved core: {result.output['core_name']}")
   print(f"Files: {len(result.output['files'])}")
   print(f"Dependencies: {result.output['dependencies']}")
