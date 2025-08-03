# Shared Module Test Report

## 📋 **Test Summary**

**Generated**: 2025-08-03 21:52:10
**Overall Status**: FAILED
**Success Rate**: 88.9%
**Total Tests**: 9
**Passed**: 8
**Failed**: 1
**Total Execution Time**: 0.67s

## 🧪 **Test Results**

### Unit Tests
- **Status**: {'tests/features/shared/test_base_entity.py': {'status': 'FAILED', 'exit_code': <ExitCode.TESTS_FAILED: 1>}}
- **Execution Time**: 0.26s

### Integration Tests  
- **Status**: {'service_integration': {'status': 'PASSED', 'execution_time': 0.1}, 'tool_integration': {'status': 'PASSED', 'execution_time': 0.1}, 'command_integration': {'status': 'PASSED', 'execution_time': 0.1}, 'cross_feature_integration': {'status': 'PASSED', 'execution_time': 0.1}}
- **Execution Time**: 0.41s

### Performance Tests
- **Status**: {'entity_creation_performance': {'status': 'PASSED', 'execution_time': 0.007637739181518555, 'entities_created': 1000, 'avg_time_per_entity': 7.637739181518554e-06}, 'service_operation_performance': {'status': 'PASSED', 'execution_time': 9.5367431640625e-07}, 'tool_execution_performance': {'status': 'PASSED', 'execution_time': 0.0}, 'command_processing_performance': {'status': 'PASSED', 'execution_time': 0.0}}
- **Execution Time**: 0.01s

## 📊 **Detailed Results**

### Unit Test Details
- **tests/features/shared/test_base_entity.py**: FAILED

### Integration Test Details
- **service_integration**: PASSED
- **tool_integration**: PASSED
- **command_integration**: PASSED
- **cross_feature_integration**: PASSED

### Performance Test Details
- **entity_creation_performance**: PASSED (0.008s)
- **service_operation_performance**: PASSED (0.000s)
- **tool_execution_performance**: PASSED (0.000s)
- **command_processing_performance**: PASSED (0.000s)
