===============
Getting Started
===============

This guide will help you get started with dv-flow-libfusesoc.

Prerequisites
=============

System Requirements
-------------------

* Python 3.8 or later
* pip package manager
* Git (for cloning FuseSoC cores)

Required Knowledge
------------------

* Basic understanding of HDL (Verilog/SystemVerilog/VHDL)
* Familiarity with FuseSoC core files (.core format)
* Experience with at least one HDL simulator (Icarus, Verilator, etc.)

Installation
============

Install from PyPI
-----------------

The easiest way to install dv-flow-libfusesoc:

.. code-block:: bash

   pip install dv-flow-libfusesoc

This will install:

* dv-flow-libfusesoc
* dv-flow-mgr (DV Flow Manager)
* fusesoc (FuseSoC package)
* edalize (Edalize tool interface)

Install from Source
-------------------

For development or the latest features:

.. code-block:: bash

   git clone https://github.com/your-org/dv-flow-libfusesoc.git
   cd dv-flow-libfusesoc
   pip install -e .

Verify Installation
-------------------

Check that the extension is properly registered:

.. code-block:: python

   import dv_flow.libfusesoc
   from dv_flow.libfusesoc import __ext__
   
   packages = __ext__.dvfm_packages()
   print("Registered packages:", list(packages.keys()))
   # Should print: ['fusesoc', 'fusesoc.edalize.sim', ...]

Install Simulation Tools
------------------------

You'll need at least one HDL simulator. Open-source options:

**Icarus Verilog** (Recommended for beginners)

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install iverilog
   
   # macOS
   brew install icarus-verilog
   
   # Verify
   iverilog -v

**Verilator** (High performance)

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install verilator
   
   # macOS
   brew install verilator
   
   # Verify
   verilator --version

Quick Start Tutorial
====================

Step 1: Set Up FuseSoC Workspace
---------------------------------

Create a directory for your FuseSoC workspace:

.. code-block:: bash

   mkdir -p ~/fusesoc_workspace
   cd ~/fusesoc_workspace

Step 2: Create a Simple Core
-----------------------------

Create a simple Verilog module and testbench.

**simple.v** - A basic counter module:

.. code-block:: verilog

   module simple_counter (
       input wire clk,
       input wire rst,
       output reg [7:0] count
   );
       always @(posedge clk or posedge rst) begin
           if (rst)
               count <= 8'h00;
           else
               count <= count + 1;
       end
   endmodule

**simple_tb.v** - Testbench:

.. code-block:: verilog

   module simple_tb;
       reg clk;
       reg rst;
       wire [7:0] count;
       
       simple_counter dut (
           .clk(clk),
           .rst(rst),
           .count(count)
       );
       
       initial begin
           clk = 0;
           forever #5 clk = ~clk;
       end
       
       initial begin
           $dumpfile("simple.vcd");
           $dumpvars(0, simple_tb);
           
           rst = 1;
           #20 rst = 0;
           
           #200;
           
           if (count > 0) begin
               $display("TEST PASSED: Counter value = %d", count);
           end else begin
               $display("TEST FAILED: Counter not incrementing");
           end
           
           $finish;
       end
   endmodule

**simple.core** - FuseSoC core file:

.. code-block:: yaml

   CAPI=2:
   
   name: tutorial:example:simple_counter:1.0
   description: Simple counter example
   
   filesets:
     rtl:
       files:
         - simple.v
       file_type: verilogSource
     
     tb:
       files:
         - simple_tb.v
       file_type: verilogSource
   
   targets:
     default:
       filesets: [rtl]
     
     sim:
       default_tool: icarus
       filesets: [rtl, tb]
       toplevel: simple_tb

Step 3: Run Your First Simulation
----------------------------------

Create a Python script to run the simulation:

**run_sim.py**:

.. code-block:: python

   import asyncio
   import os
   from pathlib import Path
   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams
   from dv_flow.libfusesoc.edalize_sim import (
       SimConfigure, SimConfigureParams,
       SimBuild, SimBuildParams,
       SimRun, SimRunParams
   )

   async def main():
       # Get current directory as workspace
       workspace = str(Path.cwd())
       
       # Mock runner for this example (in real DV Flow, this is provided)
       class MockRunner:
           pass
       runner = MockRunner()
       
       print("Step 1: Resolving FuseSoC core...")
       core = await CoreResolve(runner, CoreResolveParams(
           core="tutorial:example:simple_counter:1.0",
           target="sim",
           workspace=workspace
       ))
       print(f"✓ Resolved core: {core.output['core_name']}")
       print(f"  Files: {len(core.output['files'])}")
       
       print("\nStep 2: Configuring simulation...")
       config = await SimConfigure(runner, SimConfigureParams(
           core_name=core.output['core_name'],
           files=core.output['files'],
           toplevel="simple_tb",
           tool="icarus"
       ))
       print(f"✓ Configured in: {config.output['work_root']}")
       
       print("\nStep 3: Building simulation...")
       build = await SimBuild(runner, SimBuildParams(
           work_root=config.output['work_root'],
           tool=config.output['tool']
       ))
       
       if not build.output['build_success']:
           print("✗ Build failed!")
           return 1
       
       print(f"✓ Build succeeded: {build.output['executable']}")
       
       print("\nStep 4: Running simulation...")
       run = await SimRun(runner, SimRunParams(
           work_root=build.output['work_root'],
           tool=build.output['tool']
       ))
       
       if run.output['run_success']:
           print("\n✅ SIMULATION PASSED")
       else:
           print("\n❌ SIMULATION FAILED")
       
       print(f"\nLog file: {run.output['log_file']}")
       return 0

   if __name__ == "__main__":
       exit(asyncio.run(main()))

Run the script:

.. code-block:: bash

   python run_sim.py

Expected output:

.. code-block:: text

   Step 1: Resolving FuseSoC core...
   ✓ Resolved core: simple_counter
     Files: 2
   
   Step 2: Configuring simulation...
   ✓ Configured in: /tmp/edalize_work
   
   Step 3: Building simulation...
   ✓ Build succeeded: /tmp/edalize_work/simple_tb
   
   Step 4: Running simulation...
   
   ✅ SIMULATION PASSED
   
   Log file: /tmp/edalize_work/run.log

Next Steps
==========

Now that you have a working simulation, try:

1. **Add Parameters**
   
   Modify the core to accept parameters:
   
   .. code-block:: python
   
      config = await SimConfigure(runner, SimConfigureParams(
          # ... other params ...
          parameters={'WIDTH': 16}  # Change counter width
      ))

2. **Try Different Tools**
   
   Switch to Verilator:
   
   .. code-block:: python
   
      config = await SimConfigure(runner, SimConfigureParams(
          # ... other params ...
          tool="verilator"
      ))

3. **Use Real FuseSoC Cores**
   
   Add the fusesoc-cores library:
   
   .. code-block:: bash
   
      fusesoc library add fusesoc-cores https://github.com/fusesoc/fusesoc-cores
   
   Then simulate a real IP core:
   
   .. code-block:: python
   
      core = await CoreResolve(runner, CoreResolveParams(
          core="fusesoc:utils:blinky:1.0",
          target="sim",
          workspace=workspace
      ))

4. **Integrate with DV Flow**
   
   Learn how to use these tasks within a complete DV Flow workflow.

Common Issues
=============

Core Not Found
--------------

If you see "Core not found" errors:

1. Check that the .core file is in the workspace directory
2. Verify the VLNV matches the core file's ``name:`` field
3. Make sure the workspace path is correct

Build Failures
--------------

If compilation fails:

1. Check the log in the work_root directory
2. Verify your simulator is installed: ``iverilog -v`` or ``verilator --version``
3. Check for syntax errors in your HDL files
4. Ensure file types are correct in the .core file

Tool Not Found
--------------

If Edalize can't find your tool:

1. Verify the tool is in your PATH
2. Check Edalize tool mapping: some tools need specific configuration
3. Try a different tool that you know is installed

Further Reading
===============

* :doc:`usage_examples` - More complete examples
* :doc:`tasks` - Complete task reference
* :doc:`fusesoc_integration` - FuseSoC API details
* :doc:`edalize_integration` - Edalize integration guide

* `FuseSoC Documentation <https://fusesoc.readthedocs.io/>`_
* `Edalize Documentation <https://edalize.readthedocs.io/>`_
* `DV Flow Documentation <https://dv-flow.readthedocs.io/>`_
