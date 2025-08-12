#!/usr/bin/env python3
"""
Unit tests for tool helper utilities.
"""

import json
import pytest

from kickai.utils.tool_helpers import (
    create_json_response,
    extract_single_value,
    format_tool_error,
    format_tool_success,
    parse_crewai_json_input,
    parse_json_response,
    validate_required_input,
)


class TestToolHelpers:
    """Test cases for tool helper utilities."""

    def test_extract_single_value_with_json(self):
        """Test extracting single value from JSON input."""
        json_input = '{"team_id": "KTI", "user_id": "123"}'
        result = extract_single_value(json_input, 'team_id')
        assert result == "KTI"

    def test_extract_single_value_with_regular_string(self):
        """Test extracting single value from regular string input."""
        regular_input = "KTI"
        result = extract_single_value(regular_input, 'team_id')
        assert result == "KTI"

    def test_extract_single_value_with_invalid_json(self):
        """Test extracting single value from invalid JSON input."""
        invalid_json = "{invalid json}"
        result = extract_single_value(invalid_json, 'team_id')
        assert result == invalid_json

    def test_parse_crewai_json_input_with_valid_json(self):
        """Test parsing valid JSON input with multiple keys."""
        json_input = '{"team_id": "KTI", "user_id": "123"}'
        result = parse_crewai_json_input(json_input, ['team_id', 'user_id'])
        assert result == {"team_id": "KTI", "user_id": "123"}

    def test_parse_crewai_json_input_with_regular_string(self):
        """Test parsing regular string input."""
        regular_input = "KTI"
        result = parse_crewai_json_input(regular_input, ['team_id'])
        assert result == {"team_id": "KTI"}

    def test_parse_crewai_json_input_with_invalid_json(self):
        """Test parsing invalid JSON input."""
        invalid_json = "{invalid json}"
        with pytest.raises(ValueError, match="Invalid JSON format"):
            parse_crewai_json_input(invalid_json, ['team_id'])

    def test_format_tool_error(self):
        """Test format_tool_error function."""
        result = format_tool_error("Something went wrong")
        assert result == "❌ Error: Something went wrong"

    def test_format_tool_error_with_custom_type(self):
        """Test format_tool_error function with custom error type."""
        result = format_tool_error("Validation failed", "Validation Error")
        assert result == "❌ Validation Error: Validation failed"

    def test_format_tool_success(self):
        """Test format_tool_success function."""
        result = format_tool_success("Operation completed")
        assert result == "✅ Success: Operation completed"

    def test_format_tool_success_with_custom_type(self):
        """Test format_tool_success function with custom success type."""
        result = format_tool_success("Data saved", "Info")
        assert result == "✅ Info: Data saved"

    def test_validate_required_input_with_valid_input(self):
        """Test validating required input with valid value."""
        result = validate_required_input("valid input", "Field Name")
        assert result == ""

    def test_validate_required_input_with_empty_input(self):
        """Test validate_required_input with empty input."""
        result = validate_required_input("", "Field Name")
        assert result == "❌ Error: Field Name is required"

    def test_validate_required_input_with_whitespace_input(self):
        """Test validate_required_input with whitespace-only input."""
        result = validate_required_input("   ", "Field Name")
        assert result == "❌ Error: Field Name is required"

    def test_validate_required_input_with_none_input(self):
        """Test validate_required_input with None input."""
        result = validate_required_input(None, "Field Name")
        assert result == "❌ Error: Field Name is required"

    def test_create_json_response_success(self):
        """Test create_json_response with success status."""
        data = {"message": "Operation completed", "count": 5}
        result = create_json_response("success", data=data)
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["data"] == data

    def test_create_json_response_success_with_string_data(self):
        """Test create_json_response with string data."""
        data = "Operation completed successfully"
        result = create_json_response("success", data=data)
        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["data"] == data

    def test_create_json_response_error(self):
        """Test create_json_response with error status."""
        message = "Something went wrong"
        result = create_json_response("error", message=message)
        parsed = json.loads(result)
        assert parsed["status"] == "error"
        assert parsed["message"] == message

    def test_create_json_response_invalid_status(self):
        """Test create_json_response with invalid status."""
        with pytest.raises(ValueError, match="Status must be either 'success' or 'error'"):
            create_json_response("invalid", data="test")

    def test_parse_json_response_valid_json(self):
        """Test parse_json_response with valid JSON."""
        json_string = '{"status": "success", "data": "test data"}'
        result = parse_json_response(json_string)
        assert result["status"] == "success"
        assert result["data"] == "test data"

    def test_parse_json_response_invalid_json(self):
        """Test parse_json_response with invalid JSON."""
        invalid_json = "{invalid json}"
        with pytest.raises(json.JSONDecodeError):
            parse_json_response(invalid_json) 