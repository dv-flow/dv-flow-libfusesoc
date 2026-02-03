==============
Usage Examples
==============

This page provides practical examples of using dv-flow-libfusesoc.

Basic Examples
==============

Example 1: Simple Core Resolution
----------------------------------

Resolve a FuseSoC core and inspect its contents:

.. code-block:: python

   import asyncio
   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams

   async def resolve_example():
       runner = MockRunner()  # Provided by DV Flow in real use
       
       result = await CoreResolve(runner, CoreResolveParams(
           core="vendor:lib:ip_name:1.0",
           target="sim",
           workspace="/path/to/workspace"
       ))
       
       # Inspect results
       print(f"Core name: {result.output['core_name']}")
       print(f"Root: {result.output['core_root']}")
       print(f"\nFiles ({len(result.output['files'])}):")
       for file in result.output['files']:
           print(f"  {file['name']} - {file['file_type']}")
       
       print(f"\nInclude dirs ({len(result.output['include_dirs'])}):")
       for inc in result.output['include_dirs']:
           print(f"  {inc}")
       
       print(f"\nParameters:")
       for key, value in result.output['parameters'].items():
           print(f"  {key} = {value}")

   asyncio.run(resolve_example())

Example 2: Icarus Verilog Simulation
-------------------------------------

Complete simulation flow with Icarus Verilog:

.. code-block:: python

   import asyncio
   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams
   from dv_flow.libfusesoc.edalize_sim import (
       SimConfigure, SimConfigureParams,
       SimBuild, SimBuildParams,
       SimRun, SimRunParams
   )

   async def icarus_sim():
       runner = MockRunner()
       workspace = "/path/to/workspace"
       
       # Resolve
       core = await CoreResolve(runner, CoreResolveParams(
           core="myvendor:mylib:my_ip:1.0",
           target="sim",
           workspace=workspace
       ))
       
       # Configure for Icarus
       config = await SimConfigure(runner, SimConfigureParams(
           core_name=core.output['core_name'],
           files=core.output['files'],
           include_dirs=core.output['include_dirs'],
           toplevel="my_ip_tb",
           tool="icarus",
           plusargs=["+dump_waves"],
           tool_options={
               'icarus': {
                   'iverilog_options': ['-g2009', '-Wall']
               }
           }
       ))
       
       # Build
       build = await SimBuild(runner, SimBuildParams(
           work_root=config.output['work_root'],
           tool="icarus"
       ))
       
       if not build.output['build_success']:
           print("Build failed!")
           return
       
       # Run
       run = await SimRun(runner, SimRunParams(
           work_root=build.output['work_root'],
           tool="icarus"
       ))
       
       print(f"Simulation {'PASSED' if run.output['run_success'] else 'FAILED'}")

   asyncio.run(icarus_sim())

Example 3: Verilator Simulation
--------------------------------

Using Verilator for high-performance simulation:

.. code-block:: python

   async def verilator_sim():
       runner = MockRunner()
       
       # Resolve core
       core = await CoreResolve(runner, CoreResolveParams(
           core="myvendor:mylib:my_ip:1.0",
           target="sim",
           workspace="/path/to/workspace"
       ))
       
       # Configure for Verilator
       config = await SimConfigure(runner, SimConfigureParams(
           core_name=core.output['core_name'],
           files=core.output['files'],
           include_dirs=core.output['include_dirs'],
           toplevel="my_ip_tb",
           tool="verilator",
           parameters={
               'DATA_WIDTH': 32,
               'DEPTH': 1024
           },
           tool_options={
               'verilator': {
                   'verilator_options': [
                       '--trace',        # Enable waveform tracing
                       '--trace-depth 2', # Trace depth
                       '-Wall',          # All warnings
                       '-O3'             # Optimize
                   ]
               }
           }
       ))
       
       # Build with Verilator
       build = await SimBuild(runner, SimBuildParams(
           work_root=config.output['work_root'],
           tool="verilator"
       ))
       
       # Run
       run = await SimRun(runner, SimRunParams(
           work_root=build.output['work_root'],
           tool="verilator",
           runtime_plusargs=['+trace']
       ))
       
       return run.output['run_success']

Advanced Examples
=================

Example 4: Using Multiple Libraries
------------------------------------

Add custom core libraries:

.. code-block:: python

   async def multi_library_example():
       runner = MockRunner()
       
       result = await CoreResolve(runner, CoreResolveParams(
           core="myvendor:mylib:soc:1.0",
           target="sim",
           workspace="/path/to/workspace",
           libraries={
               'custom_ips': '/path/to/custom/cores',
               'vendor_ips': '/path/to/vendor/cores',
               'open_ips': '/path/to/open/cores'
           }
       ))
       
       print(f"Resolved core with {len(result.output['dependencies'])} dependencies")
       for dep in result.output['dependencies']:
           print(f"  - {dep}")

Example 5: Parameterized Simulation
------------------------------------

Run multiple simulations with different parameters:

.. code-block:: python

   async def parameterized_sim():
       runner = MockRunner()
       
       # Resolve once
       core = await CoreResolve(runner, CoreResolveParams(
           core="myvendor:mylib:fifo:1.0",
           target="sim",
           workspace="/path/to/workspace"
       ))
       
       # Test different configurations
       configs = [
           {'DEPTH': 16, 'WIDTH': 8},
           {'DEPTH': 32, 'WIDTH': 16},
           {'DEPTH': 64, 'WIDTH': 32},
       ]
       
       results = []
       for params in configs:
           print(f"\nTesting with {params}...")
           
           # Configure
           config = await SimConfigure(runner, SimConfigureParams(
               core_name=f"fifo_{params['DEPTH']}x{params['WIDTH']}",
               files=core.output['files'],
               toplevel="fifo_tb",
               tool="verilator",
               parameters=params
           ))
           
           # Build
           build = await SimBuild(runner, SimBuildParams(
               work_root=config.output['work_root'],
               tool="verilator"
           ))
           
           # Run
           run = await SimRun(runner, SimRunParams(
               work_root=build.output['work_root'],
               tool="verilator"
           ))
           
           results.append({
               'params': params,
               'success': run.output['run_success']
           })
       
       # Summary
       print("\n=== Results ===")
       for r in results:
           status = "✓" if r['success'] else "✗"
           print(f"{status} {r['params']}")

Example 6: Error Handling
--------------------------

Proper error handling and diagnostics:

.. code-block:: python

   async def robust_sim():
       runner = MockRunner()
       
       try:
           # Resolve
           core = await CoreResolve(runner, CoreResolveParams(
               core="myvendor:mylib:my_ip:1.0",
               target="sim",
               workspace="/path/to/workspace"
           ))
       except Exception as e:
           print(f"Core resolution failed: {e}")
           return False
       
       try:
           # Configure
           config = await SimConfigure(runner, SimConfigureParams(
               core_name=core.output['core_name'],
               files=core.output['files'],
               toplevel="my_ip_tb",
               tool="icarus"
           ))
           
           if not config.output['configured']:
               print("Configuration failed!")
               return False
       
       except Exception as e:
           print(f"Configuration error: {e}")
           return False
       
       try:
           # Build
           build = await SimBuild(runner, SimBuildParams(
               work_root=config.output['work_root'],
               tool="icarus"
           ))
           
           if not build.output['build_success']:
               print("Build failed! Check logs in:", build.output['work_root'])
               # Could read and print build logs here
               return False
       
       except Exception as e:
           print(f"Build error: {e}")
           return False
       
       try:
           # Run
           run = await SimRun(runner, SimRunParams(
               work_root=build.output['work_root'],
               tool="icarus"
           ))
           
           if run.output['run_success']:
               print("✅ Simulation PASSED")
               return True
           else:
               print("❌ Simulation FAILED")
               print(f"Log: {run.output['log_file']}")
               return False
       
       except Exception as e:
           print(f"Runtime error: {e}")
           return False

Integration Examples
====================

Example 7: Integration with DV Flow
------------------------------------

Using tasks in a DV Flow workflow file:

.. code-block:: yaml

   # my_flow.dv
   package:
     name: my_project
     
     imports:
     - name: fusesoc
     - name: fusesoc.edalize.sim
     
     tasks:
     - name: resolve_uart
       task: fusesoc.CoreResolve
       params:
         core: "myvendor:uart:uart16550:1.0"
         target: "sim"
         workspace: "${workspace_dir}"
     
     - name: config_sim
       task: fusesoc.edalize.sim.SimConfigure
       params:
         core_name: "${resolve_uart.core_name}"
         files: "${resolve_uart.files}"
         toplevel: "uart_tb"
         tool: "icarus"
         parameters:
           BAUD_RATE: 115200
     
     - name: build_sim
       task: fusesoc.edalize.sim.SimBuild
       params:
         work_root: "${config_sim.work_root}"
         tool: "${config_sim.tool}"
     
     - name: run_sim
       task: fusesoc.edalize.sim.SimRun
       params:
         work_root: "${build_sim.work_root}"
         tool: "${build_sim.tool}"

Example 8: Custom Task Integration
-----------------------------------

Creating a custom task that uses CoreResolve:

.. code-block:: python

   from pydantic import BaseModel
   from typing import Dict, Any
   from dv_flow.libfusesoc.fusesoc_core_resolve import CoreResolve, CoreResolveParams

   class CustomAnalysisParams(BaseModel):
       core: str
       workspace: str
       target: str = "sim"

   class CustomAnalysisOutput(BaseModel):
       file_count: int
       verilog_files: int
       systemverilog_files: int
       total_lines: int

   class CustomAnalysisTask:
       """Analyze a FuseSoC core's file statistics"""
       
       async def __call__(self, runner, params: CustomAnalysisParams):
           # First resolve the core
           core_result = await CoreResolve(runner, CoreResolveParams(
               core=params.core,
               target=params.target,
               workspace=params.workspace
           ))
           
           # Analyze the files
           files = core_result.output['files']
           verilog_count = sum(1 for f in files if f['file_type'] == 'verilogSource')
           sv_count = sum(1 for f in files if f['file_type'] == 'systemVerilogSource')
           
           # Count lines (simplified)
           total_lines = 0
           for file in files:
               try:
                   with open(file['name']) as f:
                       total_lines += sum(1 for line in f)
               except:
                   pass
           
           return CustomAnalysisOutput(
               file_count=len(files),
               verilog_files=verilog_count,
               systemverilog_files=sv_count,
               total_lines=total_lines
           )

Real-World Examples
===================

Example 9: UART Simulation
--------------------------

Complete UART core simulation:

.. code-block:: python

   async def uart_example():
       """Simulate a UART core with multiple test patterns"""
       runner = MockRunner()
       workspace = "/path/to/workspace"
       
       # Resolve UART core
       core = await CoreResolve(runner, CoreResolveParams(
           core="opencores:uart:uart16550:1.0",
           target="sim",
           workspace=workspace
       ))
       
       test_cases = [
           {'name': 'basic', 'baud': 9600, 'data_bits': 8},
           {'name': 'fast', 'baud': 115200, 'data_bits': 8},
           {'name': 'wide', 'baud': 115200, 'data_bits': 16},
       ]
       
       for test in test_cases:
           print(f"\nRunning test: {test['name']}")
           
           config = await SimConfigure(runner, SimConfigureParams(
               core_name=f"uart_{test['name']}",
               files=core.output['files'],
               toplevel="uart_tb",
               tool="verilator",
               parameters={
                   'BAUD_RATE': test['baud'],
                   'DATA_WIDTH': test['data_bits']
               },
               plusargs=[
                   f"+testname={test['name']}",
                   f"+baud_rate={test['baud']}"
               ]
           ))
           
           build = await SimBuild(runner, SimBuildParams(
               work_root=config.output['work_root'],
               tool="verilator"
           ))
           
           if not build.output['build_success']:
               print(f"  ✗ Build failed for {test['name']}")
               continue
           
           run = await SimRun(runner, SimRunParams(
               work_root=build.output['work_root'],
               tool="verilator"
           ))
           
           if run.output['run_success']:
               print(f"  ✓ Test {test['name']} PASSED")
           else:
               print(f"  ✗ Test {test['name']} FAILED")

Example 10: SoC Subsystem Simulation
-------------------------------------

Simulating a complete SoC subsystem:

.. code-block:: python

   async def soc_subsystem_example():
       """Simulate an SoC with multiple IP cores"""
       runner = MockRunner()
       workspace = "/path/to/workspace"
       
       # Resolve the top-level SoC core (includes dependencies)
       soc = await CoreResolve(runner, CoreResolveParams(
           core="mycompany:soc:ahb_subsystem:1.0",
           target="sim",
           workspace=workspace,
           libraries={
               'vendor_ips': '/path/to/vendor/ips',
               'internal_ips': '/path/to/internal/ips'
           }
       ))
       
       print(f"SoC subsystem resolved:")
       print(f"  Main core: {soc.output['core_name']}")
       print(f"  Dependencies: {len(soc.output['dependencies'])}")
       for dep in soc.output['dependencies']:
           print(f"    - {dep}")
       
       # Configure simulation
       config = await SimConfigure(runner, SimConfigureParams(
           core_name=soc.output['core_name'],
           files=soc.output['files'],
           include_dirs=soc.output['include_dirs'],
           toplevel="ahb_subsystem_tb",
           tool="verilator",
           parameters={
               'CLK_FREQ': 100_000_000,
               'NUM_MASTERS': 4,
               'NUM_SLAVES': 8
           },
           tool_options={
               'verilator': {
                   'verilator_options': [
                       '--trace',
                       '--trace-structs',
                       '-O3',
                       '-Wall'
                   ]
               }
           }
       ))
       
       # Build (may take a while for large designs)
       print("\nBuilding (this may take a few minutes)...")
       build = await SimBuild(runner, SimBuildParams(
           work_root=config.output['work_root'],
           tool="verilator"
       ))
       
       if not build.output['build_success']:
           print("Build failed!")
           return
       
       # Run regression tests
       test_vectors = [
           'basic_read_write',
           'burst_transfers',
           'error_conditions',
           'multi_master'
       ]
       
       for test in test_vectors:
           print(f"\nRunning test: {test}")
           run = await SimRun(runner, SimRunParams(
               work_root=build.output['work_root'],
               tool="verilator",
               runtime_plusargs=[
                   f"+test={test}",
                   '+verbose=1',
                   f"+seed={hash(test)}"
               ]
           ))
           
           status = "✓ PASS" if run.output['run_success'] else "✗ FAIL"
           print(f"  {status}")

Tips and Best Practices
========================

Performance Optimization
------------------------

1. **Cache core resolution**: Resolve once, reuse for multiple simulations
2. **Use Verilator for speed**: Much faster than Icarus for large designs
3. **Incremental builds**: Edalize supports incremental compilation
4. **Parallel testing**: Run multiple test configurations in parallel

.. code-block:: python

   # Example: Parallel test execution
   import asyncio

   async def run_parallel_tests(test_configs):
       tasks = [run_single_test(config) for config in test_configs]
       results = await asyncio.gather(*tasks)
       return results

Debugging Tips
--------------

1. **Enable waveforms**: Use ``+dump_waves`` plusarg or tool-specific options
2. **Increase verbosity**: Add ``+verbose`` or tool debug flags
3. **Check logs**: Always examine the log file on failures
4. **Verify file paths**: Ensure all files in the core are accessible

.. code-block:: python

   # Debug configuration
   config = await SimConfigure(runner, SimConfigureParams(
       # ... other params ...
       plusargs=['+dump_waves', '+verbose=2'],
       tool_options={
           'icarus': {
               'iverilog_options': ['-g2009', '-Wall', '-Winfloop']
           }
       }
   ))

Workspace Management
--------------------

1. **Use separate workspaces**: Different projects in different directories
2. **Clean periodically**: Remove old build artifacts
3. **Version control .core files**: Track your core definitions
4. **Document libraries**: Keep a manifest of external libraries

.. code-block:: python

   # Workspace organization example
   workspace_layout = """
   /project_root/
     fusesoc_workspace/
       libraries/
         vendor_a/
         vendor_b/
         internal/
       cores/
         my_core.core
       work/
         (build artifacts - in .gitignore)
   """
