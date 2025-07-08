# KICKAI Development Scripts

This directory contains development and quality assurance scripts for the KICKAI project.

## 🛠️ Available Scripts

### 1. `check_architectural_imports.py`
**Purpose**: Enforces the dependency hierarchy defined in `ARCHITECTURE.md`

**What it checks**:
- Ensures imports follow the layered architecture rules
- Prevents circular dependencies between layers
- Validates that presentation layer doesn't import from infrastructure layer
- Checks for forbidden cross-layer imports

**Usage**:
```bash
python scripts/check_architectural_imports.py
```

**Example output**:
```
🔍 Checking architectural import rules...
📁 Found 67 Python files to check

❌ Architectural import violations found:
src/telegram/unified_message_handler.py:185: Architectural violation: presentation layer cannot import from infrastructure layer. Import: src.services.team_member_service
```

### 2. `check_circular_imports.py`
**Purpose**: Detects circular imports in the codebase

**What it checks**:
- Builds a dependency graph from source code
- Finds cycles in the dependency graph
- Analyzes import complexity
- Suggests fixes for circular dependencies

**Usage**:
```bash
python scripts/check_circular_imports.py
```

**Example output**:
```
🔍 Detecting circular imports...
📊 Building dependency graph...
📁 Found 67 modules with dependencies
🔄 Detecting cycles...

❌ Circular imports detected:
Cycle 1: src.telegram.unified_command_system -> src.services.player_service -> src.telegram.player_registration_handler
```

### 3. `check_in_function_imports.py`
**Purpose**: Detects problematic imports inside functions

**What it checks**:
- Finds imports that occur inside function definitions
- Identifies potential circular dependencies
- Categorizes violations by severity
- Suggests fixes for each violation type

**Usage**:
```bash
python scripts/check_in_function_imports.py
```

**Example output**:
```
🔍 Checking for in-function imports...
📁 Found 67 Python files to check

⚠️  Found 5 in-function imports:

HIGH Severity (2 violations):
📄 src/telegram/unified_message_handler.py:227
   Import: src.services.access_control_service
   Function: is_leadership_chat
   💡 Move import to top-level and use dependency injection
```

### 4. `check_test_coverage.py`
**Purpose**: Ensures adequate test coverage

**What it checks**:
- Runs pytest with coverage reporting
- Checks coverage against minimum thresholds
- Identifies untested files
- Provides coverage analysis by module type

**Usage**:
```bash
python scripts/check_test_coverage.py
```

**Example output**:
```
🧪 Checking test coverage...
📊 Running test coverage...
📈 Coverage Results:
src/services/player_service.py    85%   15-20,25-30
src/telegram/unified_command_system.py    70%   45-50

⚠️  Found 3 coverage issues:
📊 Coverage Threshold Issues:
📄 src/telegram/unified_command_system.py: 70% coverage (minimum 75%)
```

## 🔧 Integration with Pre-commit

These scripts are integrated into the pre-commit hooks defined in `.pre-commit-config.yaml`:

- **Architectural imports**: Checked on every commit
- **Circular imports**: Checked on every commit  
- **In-function imports**: Checked on every commit
- **Test coverage**: Checked manually or in CI/CD

## 📋 Running All Checks

To run all quality checks at once:

```bash
# Run pre-commit hooks (includes all checks)
pre-commit run --all-files

# Or run individual scripts
python scripts/check_architectural_imports.py
python scripts/check_circular_imports.py
python scripts/check_in_function_imports.py
python scripts/check_test_coverage.py
```

## 🎯 Fixing Violations

### Architectural Violations
1. **Review dependency hierarchy** in `ARCHITECTURE.md`
2. **Use interfaces** for cross-layer communication
3. **Implement dependency injection** for tight coupling
4. **Move imports to top-level** where possible

### Circular Imports
1. **Extract shared logic** to common modules
2. **Use event-driven communication** between layers
3. **Implement interfaces** to break direct dependencies
4. **Refactor module boundaries** to reduce coupling

### In-Function Imports
1. **Move imports to top-level** when possible
2. **Use dependency injection** for required dependencies
3. **Extract shared logic** to avoid repeated imports
4. **Consider lazy loading** for heavy dependencies

### Coverage Issues
1. **Add unit tests** for uncovered code paths
2. **Write integration tests** for complex workflows
3. **Mock external dependencies** in tests
4. **Focus on business logic** coverage first

## 🔍 Configuration

Scripts can be configured by modifying:

- **Architectural layers**: Update `ARCHITECTURAL_LAYERS` in `check_architectural_imports.py`
- **Allowed imports**: Modify `ALLOWED_IN_FUNCTION_IMPORTS` in `check_in_function_imports.py`
- **Coverage thresholds**: Update thresholds in `check_test_coverage.py`
- **Pre-commit hooks**: Modify `.pre-commit-config.yaml`

## 📊 Continuous Integration

These scripts are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Quality Checks
  run: |
    python scripts/check_architectural_imports.py
    python scripts/check_circular_imports.py
    python scripts/check_in_function_imports.py
    python scripts/check_test_coverage.py
```

## 🚀 Best Practices

1. **Run checks frequently** during development
2. **Fix violations early** before they accumulate
3. **Use pre-commit hooks** to catch issues before commit
4. **Review violations carefully** - some may be false positives
5. **Update scripts** as the architecture evolves
6. **Document exceptions** when violations are intentional

## 📚 Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architectural principles and rules
- [pyproject.toml](../pyproject.toml) - Linting configuration
- [.pre-commit-config.yaml](../.pre-commit-config.yaml) - Pre-commit hooks
- [README.md](../README.md) - Project overview 