#!/usr/bin/env python3
"""
Context Optimizer for CrewAI Execution

This module implements CrewAI best practices for minimal execution context,
reducing token usage and improving agent performance.
"""

import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime

from kickai.core.enums import AgentRole

logger = logging.getLogger(__name__)


class ContextOptimizer:
    """
    Optimizes execution context for CrewAI agents following best practices:
    
    1. Minimal Necessary Context - Only data agents actually need
    2. No Duplicate Data - Single source of truth for all fields
    3. Context Filtering - Agent-specific context subsets
    4. Memory References - Use IDs instead of embedded data
    """

    # Define minimal context fields for each agent type
    AGENT_CONTEXT_REQUIREMENTS: Dict[AgentRole, Set[str]] = {
        AgentRole.MESSAGE_PROCESSOR: {
            "telegram_id",
            "team_id", 
            "chat_id",
            "chat_type",
            "message_text",
            "username"
        },
        AgentRole.HELP_ASSISTANT: {
            "telegram_id",
            "team_id",
            "chat_type",
            "message_text",
            "username"
        },
        AgentRole.PLAYER_COORDINATOR: {
            "telegram_id",
            "team_id",
            "chat_id", 
            "chat_type",
            "message_text",
            "username",
            "is_registered",
            "is_player"
        },
        AgentRole.TEAM_ADMINISTRATOR: {
            "telegram_id",
            "team_id",
            "chat_id",
            "chat_type", 
            "message_text",
            "username",
            "is_registered",
            "is_team_member"
        },
        AgentRole.SQUAD_SELECTOR: {
            "telegram_id",
            "team_id",
            "chat_id",
            "message_text",
            "username"
        },
        AgentRole.NLP_PROCESSOR: {
            "telegram_id",
            "team_id",
            "chat_type",
            "message_text",
            "username"
        }
    }

    @classmethod
    def create_minimal_context(
        self,
        telegram_id: int,
        team_id: str,
        chat_id: str,
        chat_type: str,
        message_text: str,
        username: str,
        **optional_fields
    ) -> Dict[str, Any]:
        """
        Create minimal execution context following CrewAI best practices.
        
        Returns only essential fields with no duplication or nesting.
        """
        context = {
            "telegram_id": telegram_id,
            "team_id": team_id,
            "chat_id": chat_id,
            "chat_type": chat_type,
            "message_text": message_text,
            "username": username,
        }
        
        # Add optional fields if provided (but keep minimal)
        allowed_optional = {
            "is_registered", "is_player", "is_team_member", 
            "conversation_id", "has_history"
        }
        
        for key, value in optional_fields.items():
            if key in allowed_optional:
                context[key] = value
        
        return context

    @classmethod 
    def filter_context_for_agent(
        self, 
        context: Dict[str, Any], 
        agent_role: AgentRole
    ) -> Dict[str, Any]:
        """
        Filter context to include only fields needed by specific agent.
        
        This implements CrewAI's "Minimal Necessary Context" principle.
        """
        required_fields = self.AGENT_CONTEXT_REQUIREMENTS.get(
            agent_role, 
            {"telegram_id", "team_id", "message_text"}  # Minimal fallback
        )
        
        filtered_context = {}
        for field in required_fields:
            if field in context:
                filtered_context[field] = context[field]
        
        logger.debug(
            f"Filtered context for {agent_role.value}: "
            f"{len(filtered_context)} fields (reduced from {len(context)})"
        )
        
        return filtered_context

    @classmethod
    def create_conversation_reference(
        self,
        telegram_id: int,
        team_id: str,
        has_previous: bool = False,
        last_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create minimal conversation reference instead of full history.
        
        Uses references instead of embedded data to reduce context size.
        """
        ref = {
            "conversation_id": f"{team_id}_{telegram_id}_{int(datetime.now().timestamp())}",
            "has_previous": has_previous,
        }
        
        if last_command:
            ref["last_command"] = last_command
            
        return ref

    @classmethod
    def summarize_response(self, response: str, max_length: int = 50) -> str:
        """
        Summarize responses for history storage instead of full content.
        
        Prevents massive context bloat from full response histories.
        """
        if len(response) <= max_length:
            return response
            
        # For structured responses, extract just the type
        if response.startswith('{"'):
            try:
                import json
                data = json.loads(response)
                if "message" in data:
                    return f"JSON response: {data.get('message', 'success')[:30]}..."
                elif "data" in data:
                    return f"Data response: {len(data['data'])} items"
                else:
                    return "JSON response"
            except:
                pass
        
        # For text responses, truncate intelligently
        return response[:max_length] + "..." if len(response) > max_length else response

    @classmethod
    def optimize_execution_context(
        self,
        raw_context: Dict[str, Any],
        target_agent: Optional[AgentRole] = None
    ) -> Dict[str, Any]:
        """
        Full context optimization pipeline:
        1. Remove duplicates and nested structures
        2. Filter for target agent if specified
        3. Replace heavy data with references
        4. Validate result
        """
        # Step 1: Remove known duplication issues
        optimized = {}
        
        # Remove user_id if it exists (should be gone but safety check)
        # Remove memory_context (replaced with minimal references)
        excluded_keys = {"user_id", "memory_context", "source", "timestamp", "metadata"}
        
        for key, value in raw_context.items():
            if key not in excluded_keys:
                optimized[key] = value
        
        # Step 2: Filter for specific agent if provided
        if target_agent:
            optimized = self.filter_context_for_agent(optimized, target_agent)
        
        # Step 3: Add minimal conversation reference using optimized memory manager
        telegram_id = optimized.get("telegram_id")
        team_id = optimized.get("team_id")
        
        if telegram_id and team_id:
            from kickai.agents.utils.memory_manager import get_memory_manager
            memory_manager = get_memory_manager(team_id)
            conversation_ref = memory_manager.get_conversation_reference(telegram_id)
            optimized.update(conversation_ref)
        
        # Step 4: Validate result size
        original_size = len(str(raw_context))
        optimized_size = len(str(optimized))
        
        if optimized_size > 1000:  # Still too large
            logger.warning(
                f"Context still large ({optimized_size} chars) after optimization. "
                f"Consider further filtering."
            )
        
        reduction_percent = (1 - optimized_size/original_size) * 100 if original_size > 0 else 0
        
        logger.info(
            f"Context optimized: {original_size} → {optimized_size} chars "
            f"({reduction_percent:.1f}% reduction)"
        )
        
        return optimized