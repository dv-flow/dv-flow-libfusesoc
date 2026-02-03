# Contributing to dv-flow-libfusesoc

Thank you for your interest in contributing to dv-flow-libfusesoc! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or later
- Git
- At least one HDL simulator (Icarus Verilog or Verilator recommended for testing)

### Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/dv-flow/dv-flow-libfusesoc.git
   cd dv-flow-libfusesoc
   ```

2. **Set up development environment**

   ```bash
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in editable mode with dependencies
   pip install -e .
   
   # Or use ivpm for full dependency management
   pip install ivpm
   ivpm update -a -d default-dev
   ```

3. **Install testing dependencies**

   ```bash
   pip install pytest pytest-cov
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

   - Write clean, documented code
   - Follow existing code style
   - Add docstrings to new functions/classes
   - Keep changes focused and atomic

3. **Add tests**

   - All new functionality must have tests
   - Tests should be in the appropriate directory:
     - `tests/unit/` - Unit tests for individual modules
     - `tests/integration/` - Integration tests with real tools
   - Aim for >80% code coverage

4. **Run the tests**

   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=dv_flow.libfusesoc --cov-report=html
   
   # Run specific test file
   pytest tests/unit/test_fusesoc_manager.py
   ```

5. **Update documentation**

   If your changes affect the public API:
   
   - Update docstrings
   - Update relevant .rst files in `docs/`
   - Add examples if appropriate

   Build docs locally to verify:
   
   ```bash
   cd docs
   make html
   # Open docs/_build/html/index.html in browser
   ```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add type hints where appropriate
- Use Pydantic models for task parameters and outputs

Example:

```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class MyTaskParams(BaseModel):
    """Parameters for MyTask.
    
    Attributes:
        core: Core VLNV identifier
        workspace: Path to FuseSoC workspace
        options: Optional configuration options
    """
    core: str
    workspace: str
    options: Optional[Dict[str, Any]] = None
```

### Testing Guidelines

#### Test Structure

```python
def test_feature_name():
    """Test description explaining what is being tested."""
    # Arrange - set up test data
    params = MyParams(...)
    
    # Act - execute the code being tested
    result = my_function(params)
    
    # Assert - verify the results
    assert result.success
    assert result.output['key'] == expected_value
```

#### Test Isolation

**Important:** All tests must be fully isolated:

- Use the `isolated_fusesoc_workspace` fixture for FuseSoC tests
- Never modify user's global FuseSoC configuration
- Clean up all temporary files after tests
- Don't depend on external state or files

Example:

```python
def test_with_isolation(isolated_fusesoc_workspace):
    """Test using isolated workspace."""
    workspace = isolated_fusesoc_workspace
    
    # All operations isolated to workspace.workspace directory
    manager = FuseSoCManager(workspace.workspace)
    # ... test code ...
```

#### Test Categories

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete workflows (may be skipped if tools unavailable)

Mark tests appropriately:

```python
import pytest

@pytest.mark.skipif(not has_tool("icarus"), reason="Icarus not installed")
def test_icarus_simulation():
    """Test that requires Icarus Verilog."""
    pass
```

## Submitting Changes

### Pull Request Process

1. **Ensure all tests pass**

   ```bash
   pytest
   ```

2. **Update documentation**

   If you've changed the API or added features, update the docs.

3. **Commit your changes**

   Use clear, descriptive commit messages:
   
   ```bash
   git commit -m "Add support for XYZ feature
   
   - Implemented ABC functionality
   - Added tests for DEF
   - Updated documentation"
   ```

4. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**

   - Go to the GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - Description of changes
     - Related issues (if any)
     - Testing performed
     - Documentation updates

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files included (check `.gitignore`)
- [ ] Changes are focused and atomic

## Project Structure

```
dv-flow-libfusesoc/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI configuration
├── docs/                       # Sphinx documentation
│   ├── index.rst
│   ├── getting_started.rst
│   ├── usage_examples.rst
│   └── ...
├── src/
│   └── dv_flow/
│       └── libfusesoc/
│           ├── __init__.py     # Version info
│           ├── __ext__.py      # Extension registration
│           ├── flow.dv         # Flow definitions
│           ├── sim_flow.dv
│           ├── fusesoc_*.py    # FuseSoC integration
│           ├── edalize_*.py    # Edalize integration
│           └── edam_builder.py
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── fixtures/               # Test data
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── ivpm.yaml                   # Dependency management
├── pyproject.toml             # Package configuration
└── README.md
```

## Common Tasks

### Adding a New Task

1. Create task file in `src/dv_flow/libfusesoc/`
2. Define Pydantic parameter and output models
3. Implement the task class with `__call__` method
4. Add task to appropriate `.dv` flow file
5. Write unit tests in `tests/unit/`
6. Add integration test if needed
7. Document in `docs/tasks.rst`

### Adding Tool Support

1. Update `edalize_sim.py` (or appropriate module)
2. Add tool-specific options handling
3. Update supported tools list in documentation
4. Add tests with the tool (or mark as skip if unavailable)

### Updating Documentation

1. Edit appropriate `.rst` file in `docs/`
2. Build locally: `cd docs && make html`
3. Review in browser: `docs/_build/html/index.html`
4. Commit documentation changes with code changes

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Tool versions (if relevant)
- Minimal code to reproduce the issue
- Expected behavior
- Actual behavior
- Error messages/stack traces

### Feature Requests

For feature requests, please describe:

- Use case and motivation
- Proposed API or interface
- Examples of how it would be used
- Alternatives considered

## Communication

- **GitHub Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For questions and general discussion

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Keep discussions on-topic

## License

By contributing to dv-flow-libfusesoc, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

If you have questions about contributing, please:

1. Check the documentation
2. Search existing issues
3. Open a new discussion or issue

Thank you for contributing to dv-flow-libfusesoc!
