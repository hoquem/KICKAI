#!/usr/bin/env python3
"""
Async Tool Metadata System for KICKAI (100% Async Architecture)

Provides standardized metadata and interfaces for async CrewAI tools
with dynamic prompt generation and context injection.

ALL TOOLS MUST BE ASYNC - Sync tools are no longer supported in 2025 architecture.
The system enforces async-only tools for native CrewAI compatibility.
"""

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from loguru import logger

from kickai.core.enums import ChatType


@dataclass
class AsyncToolMetadata:
    """Metadata for async CrewAI tools. All tools are async in 2025 architecture."""

    name: str
    description: str
    use_cases: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    is_async: bool = field(default=True, init=False)  # Always True, not settable
    standard_params: list[str] = field(default_factory=lambda: [
        "telegram_id", "team_id", "username", "chat_type"
    ])
    tool_specific_params: list[str] = field(default_factory=list)


class AsyncToolProtocol(Protocol):
    """Standard interface for all async tools in KICKAI."""

    async def __call__(
        self,
        telegram_id: int,
        team_id: str,
        username: str,
        chat_type: ChatType,
        **kwargs
    ) -> str:
        """Standard async tool signature with required context parameters."""
        ...


class AsyncToolRegistry:
    """Registry for async CrewAI tools with metadata management.

    Enforces 100% async architecture - sync tools are rejected with ValueError.
    All registered tools must use async def syntax for CrewAI 2025 compatibility.
    """

    def __init__(self):
        self.tools: dict[str, Callable] = {}
        self.metadata: dict[str, AsyncToolMetadata] = {}
        logger.info("🔧 AsyncToolRegistry initialized (async-only architecture)")

    def register_async_tool(self, tool_func: Callable) -> None:
        """Register async tool with automatic metadata extraction. ALL tools must be async."""
        try:
            # Handle both CrewAI Tool objects and regular functions
            if hasattr(tool_func, 'name'):
                # CrewAI Tool object
                tool_name = tool_func.name
                actual_func = getattr(tool_func, 'func', tool_func)
            else:
                # Regular function
                tool_name = getattr(tool_func, '__name__', 'unknown_tool')
                actual_func = tool_func

            # Validate that tool is async - ALL tools must be async
            is_async = callable(actual_func) and asyncio.iscoroutinefunction(actual_func)

            if not is_async:
                logger.error(f"❌ ARCHITECTURE VIOLATION: Tool {tool_name} is not async - ALL tools must be async in 2025 architecture")
                raise ValueError(f"Tool {tool_name} must be async - sync tools are no longer supported")

            self.tools[tool_name] = tool_func
            self.metadata[tool_name] = self._extract_metadata(tool_func, tool_name, actual_func)
            # is_async is always True now - no need to set it

            logger.debug(f"✅ Registered async tool: {tool_name}")

        except Exception as e:
            # Get tool name for error logging
            tool_name = 'unknown'
            try:
                if hasattr(tool_func, 'name'):
                    tool_name = tool_func.name
                elif hasattr(tool_func, '__name__'):
                    tool_name = tool_func.__name__
            except Exception:
                pass
            logger.error(f"❌ Failed to register tool {tool_name}: {e}")
            # Don't re-raise other types of errors - continue processing

    def _extract_metadata(self, tool_func: Callable, tool_name: str, actual_func: Callable) -> AsyncToolMetadata:
        """Extract metadata from tool function."""
        try:
            # Extract docstring from the actual function
            docstring = getattr(actual_func, '__doc__', None) or getattr(tool_func, '__doc__', None) or f"Tool: {tool_name}"
            description = docstring.split('\n')[0].strip()

            # Extract use cases from docstring
            use_cases = self._extract_use_cases(docstring)

            # Extract permissions from docstring
            permissions = self._extract_permissions(docstring)

            # Extract tool-specific parameters
            tool_specific_params = self._extract_tool_params(actual_func)

            return AsyncToolMetadata(
                name=tool_name,
                description=description,
                use_cases=use_cases,
                permissions=permissions,
                tool_specific_params=tool_specific_params
            )

        except Exception as e:
            logger.warning(f"⚠️ Failed to extract metadata for {tool_name}: {e}")
            return AsyncToolMetadata(
                name=tool_name,
                description=f"Tool: {tool_name}"
            )

    def _extract_use_cases(self, docstring: str) -> list[str]:
        """Extract use cases from tool docstring."""
        use_cases = []
        lines = docstring.split('\n')

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['use when:', 'use for:', 'commands:']):
                # Extract the part after the colon
                if ':' in line:
                    cases = line.split(':', 1)[1].strip()
                    # Split by common separators
                    for case in cases.replace(',', ';').split(';'):
                        case = case.strip().strip('"\'')
                        if case:
                            use_cases.append(case)

        return use_cases

    def _extract_permissions(self, docstring: str) -> list[str]:
        """Extract permissions from tool docstring."""
        permissions = []
        lines = docstring.split('\n')

        for line in lines:
            line = line.strip().lower()
            if 'requires:' in line or 'permission:' in line:
                if 'leadership' in line:
                    permissions.append('leadership')
                elif 'admin' in line:
                    permissions.append('admin')
                elif 'player' in line:
                    permissions.append('player')

        return permissions

    def _extract_tool_params(self, tool_func: Callable) -> list[str]:
        """Extract tool-specific parameters (excluding standard context)."""
        try:
            sig = inspect.signature(tool_func)
            standard_params = {"telegram_id", "team_id", "username", "chat_type"}

            tool_params = []
            for param_name in sig.parameters:
                if param_name not in standard_params and param_name != 'kwargs':
                    tool_params.append(param_name)

            return tool_params

        except Exception as e:
            logger.warning(f"⚠️ Failed to extract parameters: {e}")
            return []

    def get_tools_for_agent(self, agent_tools: list[str]) -> list[Callable]:
        """Get async tools for specific agent by tool names."""
        tools = []
        for tool_name in agent_tools:
            if tool_name in self.tools:
                tools.append(self.tools[tool_name])
            else:
                logger.warning(f"⚠️ Tool {tool_name} not found in async registry")

        return tools

    def get_metadata_for_tools(self, tool_names: list[str]) -> dict[str, AsyncToolMetadata]:
        """Get metadata for specific tools."""
        return {
            name: self.metadata[name]
            for name in tool_names
            if name in self.metadata
        }

    def generate_tools_documentation(self, tool_names: list[str]) -> str:
        """Generate documentation for a set of tools."""
        docs = []

        for tool_name in tool_names:
            if tool_name in self.metadata:
                meta = self.metadata[tool_name]
                doc_line = f"• {meta.name}: {meta.description}"

                if meta.use_cases:
                    doc_line += f"\n  Use for: {', '.join(meta.use_cases)}"

                if meta.permissions:
                    doc_line += f"\n  Requires: {', '.join(meta.permissions)} permissions"

                if meta.tool_specific_params:
                    doc_line += f"\n  Parameters: {', '.join(meta.tool_specific_params)}"

                docs.append(doc_line)
            else:
                docs.append(f"• {tool_name}: Tool documentation not available")

        return '\n'.join(docs)

    def validate_async_tools(self, tool_names: list[str]) -> dict[str, bool]:
        """Validate that tools are properly async. ALL tools MUST be async in 2025 architecture."""
        validation = {}
        sync_tools_found = []

        for tool_name in tool_names:
            if tool_name in self.tools:
                tool_func = self.tools[tool_name]
                # Handle both CrewAI Tool objects and regular functions
                if hasattr(tool_func, 'func'):
                    actual_func = tool_func.func
                else:
                    actual_func = tool_func

                is_async = asyncio.iscoroutinefunction(actual_func)
                validation[tool_name] = is_async

                if not is_async:
                    sync_tools_found.append(tool_name)
            else:
                validation[tool_name] = False

        # Log warning if any sync tools found - ALL tools should be async now
        if sync_tools_found:
            logger.warning(f"⚠️ ARCHITECTURE VIOLATION: Found sync tools (should be async): {sync_tools_found}")
            logger.warning("🔧 All tools MUST be async in 2025 architecture for CrewAI compatibility")

        return validation

    def validate_all_tools_async(self) -> bool:
        """Validate that ALL tools in the registry are async. Returns True if all async, False otherwise."""
        all_tool_names = list(self.tools.keys())
        validation = self.validate_async_tools(all_tool_names)

        sync_tools = [name for name, is_async in validation.items() if not is_async]
        total_tools = len(validation)
        async_tools_count = sum(validation.values())

        if sync_tools:
            logger.error(f"❌ ARCHITECTURE VIOLATION: {len(sync_tools)} sync tools found out of {total_tools} total tools")
            logger.error(f"❌ Sync tools that need conversion: {sync_tools}")
            logger.info(f"✅ Async tools: {async_tools_count}/{total_tools}")
            return False
        else:
            logger.info(f"✅ ALL TOOLS ARE ASYNC: {async_tools_count}/{total_tools} tools are properly async")
            return True

    def get_registry_stats(self) -> dict[str, Any]:
        """Get statistics about the async tool registry. All tools are now async."""
        total_tools = len(self.tools)
        # All tools are async now - no need to count
        async_tools = total_tools

        return {
            "total_tools": total_tools,
            "async_tools": async_tools,
            "sync_tools": 0,  # Always 0 - sync tools not supported
            "tools_with_metadata": len(self.metadata),
            "tools_by_permission": self._count_tools_by_permission(),
            "architecture": "100% async"
        }

    def _count_tools_by_permission(self) -> dict[str, int]:
        """Count tools by permission level."""
        permission_counts = {}

        for meta in self.metadata.values():
            for permission in meta.permissions:
                permission_counts[permission] = permission_counts.get(permission, 0) + 1

        return permission_counts


class AsyncContextInjector:
    """Inject context into async tool calls and generate dynamic prompts."""

    @staticmethod
    def create_dynamic_task_description(
        user_request: str,
        context: dict,
        tool_registry: AsyncToolRegistry,
        agent_tool_names: list[str]
    ) -> str:
        """Generate clean, token-efficient task description with optimal parameter passing instructions."""
        try:
            # Format tools with function signatures for clarity
            tool_signatures = AsyncContextInjector._format_tool_signatures(
                agent_tool_names, tool_registry, context
            )
            
            # Count available tools
            available_tools_count = len([name for name in agent_tool_names if name in tool_registry.tools])
            
            # Context-aware tool selection guidance (simplified)
            context_guidance = AsyncContextInjector._generate_context_aware_guidance(
                context['chat_type'], agent_tool_names
            )

            return f"""## CONTEXT
User: {context['username']} (ID: {context['telegram_id']})
Team: {context['team_id']}
Chat: {context['chat_type']}

## TASK
{user_request}

## CALLING PATTERN
All tools follow: tool_name({context['telegram_id']}, "{context['team_id']}", "{context['username']}", "{context['chat_type']}", ...params)

Example: add_player({context['telegram_id']}, "{context['team_id']}", "{context['username']}", "{context['chat_type']}", "John Smith", "+447123456789")

## AVAILABLE TOOLS ({available_tools_count} async tools)
{tool_signatures}

{context_guidance}

Execute the appropriate tool and return its exact output."""

        except Exception as e:
            logger.error(f"❌ Failed to create dynamic task description: {e}")
            # Fallback to basic description
            return f"""
User Request: {user_request}

Context:
- User: {context.get('username', 'unknown')} (ID: {context.get('telegram_id', 'unknown')})
- Team: {context.get('team_id', 'unknown')}
- Chat: {context.get('chat_type', 'unknown')}

Instructions: Use available tools to respond to the user's request.
"""

    @staticmethod
    def _format_tool_signatures(
        agent_tool_names: list[str], 
        tool_registry: AsyncToolRegistry, 
        context: dict
    ) -> str:
        """Format tools as function signatures for clarity."""
        try:
            signatures = []
            
            for tool_name in agent_tool_names:
                if tool_name in tool_registry.metadata:
                    meta = tool_registry.metadata[tool_name]
                    
                    # Build function signature
                    params = ["telegram_id: int", "team_id: str", "username: str", "chat_type: str"]
                    
                    # Add tool-specific parameters with types if available
                    if meta.tool_specific_params:
                        for param in meta.tool_specific_params:
                            params.append(f"{param}: str")
                    
                    signature = f"- {tool_name}({', '.join(params)})"
                    
                    # Add brief description if available
                    if meta.description:
                        # Keep description concise (first sentence only)
                        desc = meta.description.split('.')[0] + '.'
                        if len(desc) > 80:
                            desc = desc[:77] + "..."
                        signature += f"  # {desc}"
                    
                    signatures.append(signature)
                else:
                    # Fallback for tools without metadata
                    signatures.append(f"- {tool_name}(telegram_id: int, team_id: str, username: str, chat_type: str, ...)")
            
            return '\n'.join(signatures)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to format tool signatures: {e}")
            return '\n'.join([f"- {name}" for name in agent_tool_names])
    
    @staticmethod
    def _generate_context_aware_guidance(chat_type: str, agent_tool_names: list[str]) -> str:
        """Generate concise context-aware tool selection guidance."""
        try:
            # Check available tools for guidance
            has_get_my_status = 'get_my_status' in agent_tool_names
            has_active_players = 'get_active_players' in agent_tool_names
            has_list_all = 'list_team_members_and_players' in agent_tool_names
            has_player_status = 'get_player_status' in agent_tool_names
            has_update_player_field = 'update_player_field' in agent_tool_names
            has_update_multiple_fields = 'update_player_multiple_fields' in agent_tool_names

            guidance = []
            
            # Intent recognition (simplified)
            if has_get_my_status or has_player_status:
                guidance.append("👤 PERSONAL: /myinfo, /info, /status → get_my_status")
                if has_player_status:
                    guidance.append("👥 SPECIFIC: /status [name/phone] → get_player_status")
            
            # Update commands guidance
            if has_update_player_field or has_update_multiple_fields:
                if has_update_player_field:
                    guidance.append("✏️ UPDATE SINGLE: /update [field] [value] → update_player_field")
                if has_update_multiple_fields:
                    guidance.append("✏️ UPDATE MULTIPLE: bulk updates → update_player_multiple_fields")
            
            # Context-based list tools
            if has_active_players and has_list_all:
                chat_lower = chat_type.lower()
                if chat_lower in ['main', 'main_chat']:
                    guidance.append("📋 MAIN CHAT: /list → get_active_players (match planning)")
                elif chat_lower in ['leadership', 'leadership_chat']:
                    guidance.append("📋 LEADERSHIP: /list → list_team_members_and_players (full roster)")
            
            if guidance:
                return "## TOOL SELECTION\n" + "\n".join(guidance)
            else:
                return f"## CONTEXT\nChat: {chat_type} - Select appropriate tool for request"

        except Exception as e:
            logger.warning(f"⚠️ Failed to generate context guidance: {e}")
            return f"Context: {chat_type} chat"

    @staticmethod
    def validate_context(context: dict) -> bool:
        """Validate that required context is present."""
        required_keys = ['telegram_id', 'team_id', 'username', 'chat_type']
        return all(key in context and context[key] for key in required_keys)


# Global async tool registry instance
_async_tool_registry: AsyncToolRegistry | None = None


def get_async_tool_registry() -> AsyncToolRegistry:
    """Get the global async tool registry instance."""
    global _async_tool_registry
    if _async_tool_registry is None:
        _async_tool_registry = AsyncToolRegistry()
    return _async_tool_registry


def register_async_tool(tool_func: Callable) -> None:
    """Register an async tool with the global registry."""
    registry = get_async_tool_registry()
    registry.register_async_tool(tool_func)
