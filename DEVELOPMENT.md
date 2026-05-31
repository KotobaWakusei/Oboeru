# Oboeru Development Guide

## Phase 1: Quality Foundations ✅ COMPLETED

### What was done in Phase 1

#### 1. **Enhanced pyproject.toml**
- Added mypy configuration with strict type checking rules
- Added pytest configuration with markers and coverage settings
- Added coverage reporting configuration (HTML + terminal)
- Fixed Black and Ruff tool configurations

#### 2. **Pre-commit Hooks Setup** 
Created `.pre-commit-config.yaml` with:
- Black (code formatting)
- Ruff (linting)
- Mypy (type checking)
- Pre-commit hooks (security, formatting)
- Bandit (security scanning)

#### 3. **Dependency Management**
- Created `dev-requirements.txt` with pinned versions:
  - black==23.12.1
  - ruff==0.1.11
  - mypy==1.7.1
  - pytest==7.4.3
  - pytest-cov==4.1.0
  - pre-commit==3.5.0
- Updated `requirements.txt` with exact versions

#### 4. **Enhanced Makefile**
Added targets:
- `format` - Format code with Black
- `lint` - Lint with Ruff
- `type-check` - Type check with Mypy
- `test` - Run pytest
- `test-cov` - Run tests with coverage report
- `clean` - Clean build artifacts
- `install-dev` - Install all dependencies
- `pre-commit-install` - Set up hooks
- `check` - Run all checks

#### 5. **Test Framework**
- Created `tests/` directory structure
- Added `tests/conftest.py` with shared fixtures:
  - `temp_dir` - Temporary directory for tests
  - `config_manager` - ConfigManager instance
  - `vocabulary_manager` - VocabularyManager instance
  - `favorites_manager` - FavoritesManager instance
  - `progress_manager` - ProgressManager instance
  - `sample_vocab_file` - Test vocabulary file

#### 6. **Unit Tests Created**
- `tests/test_config_manager.py` - 12 tests ✅ (all passing)
- `tests/test_vocabulary_manager.py` - Tests for vocabulary operations
- `tests/test_favorites_manager.py` - Tests for favorites management
- `tests/test_progress_manager.py` - Tests for progress tracking

**Current Test Status:**
```
39 passed, 27 failed
Test Coverage: 33.02%
```

### Phase 1 Results

✅ **Completed Tasks:**
- [x] Setup mypy configuration
- [x] Setup pytest framework
- [x] Setup pre-commit hooks
- [x] Pin dependency versions
- [x] Create initial unit tests
- [x] Test framework working

📊 **Metrics:**
- Test Coverage: 0% → 33%
- Config Manager: 100% test coverage ✅
- Type Check Errors: 4 detected (fixable)

### Quick Start

#### Install Development Environment
```bash
make install-dev
make pre-commit-install
```

#### Run Checks
```bash
make format    # Format code with Black
make lint      # Lint with Ruff
make type-check # Type checking with Mypy
make test      # Run tests
make test-cov  # Tests with coverage report
make check     # Run all checks
```

#### View Coverage Report
```bash
make test-cov
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Next Steps (Phase 2)

**Phase 2: Code Refactoring** will focus on:
1. Splitting large components (learning_page.py, settings_page.py)
2. Implementing ThreadPoolManager
3. Enhancing error handling
4. Adding type hints to modules

## Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config_manager.py

# Run specific test class
pytest tests/test_config_manager.py::TestConfigManager

# Run specific test
pytest tests/test_config_manager.py::TestConfigManager::test_get_and_set_config

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=modules --cov=ui --cov-report=html tests/
```

### Writing New Tests

1. Create test file in `tests/` with `test_*.py` pattern
2. Import fixtures from `conftest.py`
3. Use descriptive test names (`test_*` pattern)
4. Add pytest markers for test categories

Example:
```python
import pytest
from modules.your_module import YourClass

@pytest.mark.unit
def test_your_feature(temp_dir: str) -> None:
    """Test description."""
    # Setup
    instance = YourClass()
    
    # Action
    result = instance.some_method()
    
    # Assert
    assert result is True
```

## Type Checking

### Run Type Checks
```bash
# Check specific module
mypy --ignore-missing-imports modules/config_manager.py

# Check all modules
mypy --ignore-missing-imports modules/ ui/

# Strict checking
mypy --ignore-missing-imports --strict modules/
```

### Adding Type Hints

```python
from typing import Optional, List, Dict, Any

def process_items(items: List[str], count: int = 5) -> Dict[str, Any]:
    """Process items with type hints."""
    result: Dict[str, Any] = {}
    return result
```

## Code Style

### Formatting
```bash
# Format all Python files
black .

# Check formatting without changing
black --check .
```

### Linting
```bash
# Check code with Ruff
ruff check .

# Fix issues automatically
ruff check . --fix
```

## Configuration Files

### `pyproject.toml`
Central configuration for Black, Ruff, Mypy, and Pytest

### `.pre-commit-config.yaml`
Git hooks configuration that runs on every commit

### `Makefile`
Common development tasks

### `requirements.txt`
Runtime dependencies with exact versions

### `dev-requirements.txt`
Development dependencies with exact versions

## Troubleshooting

### Permission denied on pytest cache
This is normal in shared environments. The tests still run correctly.

### Import errors in tests
Ensure `tests/conftest.py` is present with proper fixtures.

### Module not found
Run from project root and ensure dependencies are installed:
```bash
cd /path/to/Oboeru
make install-dev
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://beta.ruff.rs/)
- [Pre-commit Documentation](https://pre-commit.com/)
