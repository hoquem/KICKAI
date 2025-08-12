#!/usr/bin/env python3
"""
Response Formatter

This module provides smart formatting of JSON responses from agents into
human-readable text for Telegram users. The formatter maintains data
integrity throughout the system by only formatting at the presentation layer.
"""

import json
import re
from typing import Any, Dict, List, Union
from loguru import logger


class ResponseFormatter:
    """Smart formatter that converts JSON responses to human-readable text for Telegram."""
    
    def format_for_telegram(self, message: str) -> str:
        """Format JSON responses to human-readable text.
        
        :param message: The message string (JSON or plain text)
        :type message: str
        :returns: Human-readable formatted text
        :rtype: str
        
        .. note::
           Non-JSON messages pass through unchanged
        """
        if not self._is_json_response(message):
            return message
            
        try:
            data = json.loads(message)
            
            # Check for format hint in the JSON
            if isinstance(data, dict) and "_format" in data:
                return self._apply_format_template(data["_format"], data)
            
            # Use smart generic formatting
            return self._smart_format(data)
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse JSON response for formatting: {e}")
            return message  # Return as-is if parsing fails
    
    def _is_json_response(self, message: str) -> bool:
        """Check if a message appears to be a JSON response.
        
        :param message: Message to check
        :type message: str
        :returns: True if message appears to be JSON
        :rtype: bool
        """
        if not isinstance(message, str):
            return False
            
        message = message.strip()
        if not message:
            return False
            
        # Quick check for JSON-like structure
        return (message.startswith('{') and message.endswith('}')) or \
               (message.startswith('[') and message.endswith(']'))
    
    def _smart_format(self, data: Union[Dict, List, Any]) -> str:
        """Intelligently format any JSON structure.
        
        :param data: Parsed JSON data
        :type data: Union[Dict, List, Any]
        :returns: Formatted text
        :rtype: str
        """
        if isinstance(data, dict):
            return self._format_dict_response(data)
        elif isinstance(data, list):
            return self._format_list(data)
        else:
            return str(data)
    
    def _format_dict_response(self, data: Dict) -> str:
        """Format dictionary response based on standard patterns.
        
        :param data: Dictionary to format
        :type data: Dict
        :returns: Formatted text
        :rtype: str
        """
        # Handle standard tool response format
        if "status" in data:
            if data["status"] == "error":
                return f"❌ {data.get('message', 'Unknown error')}"
            elif data["status"] == "success" and "data" in data:
                return self._format_success_data(data["data"])
        
        # Handle direct data format
        return self._format_data(data)
    
    def _format_success_data(self, data: Any) -> str:
        """Format the data field from a success response.
        
        :param data: Data to format
        :type data: Any
        :returns: Formatted text
        :rtype: str
        """
        if isinstance(data, str):
            return data  # Already formatted text
        
        if isinstance(data, dict):
            # Check if it has a message field to display first
            if "message" in data:
                lines = [data["message"]]
                other_data = {k: v for k, v in data.items() if k != "message"}
                if other_data:
                    lines.append("")  # Empty line separator
                    lines.extend(self._dict_to_lines(other_data))
                return "\n".join(lines)
            else:
                return self._format_data(data)
        
        if isinstance(data, list):
            return self._format_list(data)
        
        return str(data)
    
    def _format_data(self, data: Union[Dict, List, Any]) -> str:
        """Format any data structure.
        
        :param data: Data to format
        :type data: Union[Dict, List, Any]
        :returns: Formatted text
        :rtype: str
        """
        if isinstance(data, dict):
            return "\n".join(self._dict_to_lines(data))
        elif isinstance(data, list):
            return self._format_list(data)
        else:
            return str(data)
    
    def _dict_to_lines(self, data: Dict) -> List[str]:
        """Convert dictionary to formatted lines.
        
        :param data: Dictionary to convert
        :type data: Dict
        :returns: List of formatted lines
        :rtype: List[str]
        """
        lines = []
        for key, value in data.items():
            if key.startswith("_"):  # Skip internal fields
                continue
                
            # Format key nicely
            display_key = self._format_key(key)
            
            # Format value based on type
            display_value = self._format_value(value)
            
            lines.append(f"{display_key}: {display_value}")
        
        return lines
    
    def _format_key(self, key: str) -> str:
        """Format a dictionary key for display.
        
        :param key: Raw key name
        :type key: str
        :returns: Formatted key name
        :rtype: str
        """
        # Convert snake_case to Title Case
        formatted = key.replace("_", " ").title()
        
        # Special cases for common fields
        replacements = {
            "Id": "ID",
            "Url": "URL",
            "Api": "API",
            "Ui": "UI",
            "Uuid": "UUID",
            "Http": "HTTP",
            "Html": "HTML",
        }
        
        for old, new in replacements.items():
            formatted = formatted.replace(old, new)
        
        return formatted
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display.
        
        :param value: Value to format
        :type value: Any
        :returns: Formatted value string
        :rtype: str
        """
        if isinstance(value, bool):
            return "Yes" if value else "No"
        elif isinstance(value, list):
            if not value:
                return "None"
            else:
                # Format list items with bullets
                formatted_items = [self._format_list_item_inline(item) for item in value[:5]]  # Limit to 5 items
                if len(value) > 5:
                    formatted_items.append("...")
                return "\n  • " + "\n  • ".join(formatted_items)
        elif isinstance(value, dict):
            # For nested dicts, format inline
            parts = []
            for k, v in list(value.items())[:3]:  # Limit to first 3 fields
                if not k.startswith("_"):
                    parts.append(f"{self._format_key(k)}: {self._format_simple_value(v)}")
            result = " | ".join(parts)
            if len(value) > 3:
                result += " | ..."
            return result
        elif value is None or value == "":
            return "Not provided"
        else:
            return str(value)
    
    def _format_simple_value(self, value: Any) -> str:
        """Format a value for inline display (no newlines).
        
        :param value: Value to format
        :type value: Any
        :returns: Simple formatted value
        :rtype: str
        """
        if isinstance(value, bool):
            return "Yes" if value else "No"
        elif isinstance(value, (list, dict)):
            return f"({len(value)} items)" if value else "None"
        elif value is None or value == "":
            return "Not provided"
        else:
            return str(value)
    
    def _format_list(self, data: List) -> str:
        """Format list of items.
        
        :param data: List to format
        :type data: List
        :returns: Formatted list text
        :rtype: str
        """
        if not data:
            return "No items found"
        
        lines = []
        for item in data:
            if isinstance(item, dict):
                # Format dict items (like player records)
                item_text = self._format_list_item(item)
                lines.append(f"• {item_text}")
            else:
                lines.append(f"• {self._format_simple_value(item)}")
        
        return "\n".join(lines)
    
    def _format_list_item(self, item: Dict) -> str:
        """Format a single list item dictionary.
        
        :param item: Dictionary item to format
        :type item: Dict
        :returns: Formatted item text
        :rtype: str
        """
        # Look for common identifying fields
        identifiers = ["name", "title", "id", "player_id", "match_id", "team_id"]
        main_text = None
        
        for field in identifiers:
            if field in item:
                main_text = str(item[field])
                break
        
        if not main_text:
            # Use first non-internal field
            for key, value in item.items():
                if not key.startswith("_"):
                    main_text = str(value)
                    break
        
        if not main_text:
            return "Unknown item"
        
        # Add status or other important context fields
        extras = []
        context_fields = ["status", "role", "position", "type", "state"]
        
        for field in context_fields:
            if field in item and field not in identifiers:
                value = item[field]
                if value:
                    extras.append(str(value))
        
        if extras:
            return f"{main_text} ({', '.join(extras)})"
        
        return main_text
    
    def _format_list_item_inline(self, item: Any) -> str:
        """Format a list item for inline display.
        
        :param item: Item to format
        :type item: Any
        :returns: Inline formatted item
        :rtype: str
        """
        if isinstance(item, dict):
            return self._format_list_item(item)
        else:
            return self._format_simple_value(item)
    
    def _apply_format_template(self, format_type: str, data: Dict) -> str:
        """Apply a specific format template (for future extensibility).
        
        :param format_type: Type of format to apply
        :type format_type: str
        :param data: Data to format
        :type data: Dict
        :returns: Formatted text using template
        :rtype: str
        
        .. note::
           Currently falls back to smart formatting.
           Can be extended with specific templates as needed.
        """
        # For now, fall back to smart formatting
        # This can be extended with specific templates if needed
        logger.debug(f"Format template '{format_type}' requested, using smart formatting")
        return self._smart_format(data)