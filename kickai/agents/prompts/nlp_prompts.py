#!/usr/bin/env python3
"""
NLP Prompt Template Library

This module provides a centralized, type-safe prompt template system for the
NLP Processor agent. It uses dataclasses for structure, inheritance for reusability,
and Pydantic for validation.

Key Features:
- Template inheritance for DRY principle
- Type-safe parameter validation
- Composition of prompt fragments
- Caching for performance
- Version control for prompt evolution
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from string import Template
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, field_validator

# =============================================================================
# Security and Input Sanitization
# =============================================================================


def sanitize_prompt_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent prompt injection attacks.

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized input string

    Raises:
        ValueError: If input is suspicious or too long
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Check length
    if len(value) > max_length:
        raise ValueError(f"Input too long: {len(value)} > {max_length}")

    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"```[\s\S]*?```",  # Code blocks
        r"<script[\s\S]*?</script>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"data:",  # Data URLs
        r"vbscript:",  # VBScript
        r"onload=",  # Event handlers
        r"onerror=",  # Error handlers
        r"\${.*?}",  # Template literals
        r"<%[\s\S]*?%>",  # Server-side includes
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"Suspicious pattern detected in input: {pattern[:20]}...")
            raise ValueError("Input contains potentially dangerous content")

    # Clean up excessive whitespace and control characters
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

    return value


# =============================================================================
# Type Definitions and Models
# =============================================================================


class PromptContext(BaseModel):
    """
    Base context model for all NLP prompts.
    Ensures consistent parameter validation across all tools.
    """

    telegram_id: int = Field(..., description="User's Telegram ID")
    team_id: str = Field(..., min_length=1, description="Team identifier")
    username: str = Field(..., min_length=1, description="Username")
    chat_type: str = Field(..., description="Chat context (main/leadership/private)")

    @field_validator("telegram_id")
    @classmethod
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError("telegram_id must be positive")
        return v

    @field_validator("chat_type")
    @classmethod
    def validate_chat_type(cls, v):
        valid_types = {"main", "leadership", "private"}
        if v not in valid_types:
            raise ValueError(f"chat_type must be one of: {valid_types}")
        return v


class IntentAnalysisContext(PromptContext):
    """Context model for intent recognition prompts."""

    message: str = Field(..., min_length=1, description="User message to analyze")
    conversation_history: str | None = Field(
        default="", description="Previous conversation context"
    )


class EntityExtractionContext(PromptContext):
    """Context model for entity extraction prompts."""

    message: str = Field(..., min_length=1, description="Message to extract entities from")


class RoutingContext(PromptContext):
    """Context model for routing recommendation prompts."""

    intent_data: str = Field(..., min_length=1, description="Intent analysis data")


class UpdateAnalysisContext(PromptContext):
    """Context model for update command analysis."""

    message: str = Field(..., min_length=1, description="Update command to analyze")


class PermissionValidationContext(PromptContext):
    """Context model for permission validation."""

    user_role: str = Field(..., description="User's role in the system")
    requested_action: str = Field(..., min_length=1, description="Action being requested")


class SimilarityAnalysisContext(PromptContext):
    """Context model for semantic similarity analysis."""

    message: str = Field(..., min_length=1, description="User message to analyze")
    reference_commands: str | None = Field(default="", description="Commands to compare against")


# =============================================================================
# Base Template Classes
# =============================================================================


@dataclass
class BasePromptTemplate(ABC):
    """
    Abstract base class for all prompt templates.
    Defines the common interface and shared functionality.
    """

    name: str
    version: str = "1.0"
    description: str = ""

    @abstractmethod
    def get_template(self) -> str:
        """Return the template string with placeholders."""
        pass

    @abstractmethod
    def get_context_model(self) -> type[BaseModel]:
        """Return the Pydantic model for context validation."""
        pass

    def render(self, context: dict[str, Any]) -> str:
        """
        Render the template with validated and sanitized context.

        Args:
            context: Dictionary of template variables

        Returns:
            Rendered prompt string

        Raises:
            ValueError: If context validation or sanitization fails
        """
        try:
            # Sanitize string inputs to prevent prompt injection
            sanitized_context = {}
            for key, value in context.items():
                if isinstance(value, str):
                    # Apply different length limits based on field type
                    max_length = 200 if key in ["message", "intent_data"] else 100
                    sanitized_context[key] = sanitize_prompt_input(value, max_length)
                else:
                    sanitized_context[key] = value

            # Validate context using Pydantic model
            context_model = self.get_context_model()
            validated_context = context_model(**sanitized_context)

            # Render template with validated data (fail-fast on missing variables)
            template = Template(self.get_template())
            return template.substitute(validated_context.model_dump())

        except Exception as e:
            logger.error(f"Error rendering template {self.name}: {e}")
            raise ValueError(f"Template rendering failed: {e!s}")


@dataclass
class FootballContextTemplate(BasePromptTemplate):
    """
    Base template for football-specific prompts.
    Provides common football context and instructions.
    """

    name: str = "football_context"
    version: str = "1.0"
    description: str = "Base template for football-specific prompts"

    def get_base_context(self) -> str:
        """Common football context for all prompts."""
        return """
        You are analyzing a request for the KICKAI football team management system.

        FOOTBALL CONTEXT:
        - This is a team management system for football/soccer teams
        - Users can be players, team members, or administrators
        - Different chat types have different permissions and contexts
        - System handles player registration, availability, matches, and administration
        """

    def get_analysis_guidelines(self) -> str:
        """Common analysis guidelines for football context."""
        return """
        ANALYSIS GUIDELINES:
        - Consider football-specific terminology and context
        - Understand team roles: player, team member, coach, admin
        - Chat context matters: main (general), leadership (admin), private (personal)
        - Team management operations require appropriate permissions
        """


# =============================================================================
# Specialized Prompt Templates
# =============================================================================


@dataclass
class IntentRecognitionTemplate(FootballContextTemplate):
    """Template for advanced intent recognition prompts."""

    name: str = "intent_recognition"
    description: str = "LLM-powered intent recognition for football team management"

    def get_context_model(self) -> type[BaseModel]:
        return IntentAnalysisContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        {self.get_analysis_guidelines()}

        Analyze the user's intent for this football team management request:

        MESSAGE: "$message"
        CHAT CONTEXT: $chat_type
        USER: $username
        TEAM: $team_id
        PREVIOUS CONTEXT: $conversation_history

        INTENT CATEGORIES:
        1. get_player_info - Getting player status, details, or information
        2. update_profile - Updating player/member information or settings
        3. get_team_info - Getting team lists, rosters, or member information
        4. get_help - Requesting help, guidance, or command information
        5. match_management - Match availability, attendance, or squad selection
        6. team_administration - Adding members, promotions, or administrative actions

        ANALYSIS REQUIREMENTS:
        1. Primary intent classification with confidence level (0.0-1.0)
        2. Key entities mentioned in the message
        3. Recommended agent for routing (message_processor, help_assistant, player_coordinator, team_administrator, squad_selector)
        4. Whether follow-up questions are needed
        5. Clear reasoning for your classification

        Respond with your analysis in JSON format.
        """


@dataclass
class EntityExtractionTemplate(FootballContextTemplate):
    """Template for entity extraction prompts."""

    name: str = "entity_extraction"
    description: str = "Extract football-related entities from user messages"

    def get_context_model(self) -> type[BaseModel]:
        return EntityExtractionContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        Extract football-related entities from this message:

        MESSAGE: "$message"
        CONTEXT: $chat_type chat for team $team_id

        ENTITY CATEGORIES TO EXTRACT:
        - Player positions: goalkeeper, defender, midfielder, forward, striker, centre-back, fullback, winger
        - Time references: today, tomorrow, next week, last match, current, recent
        - Availability status: available, unavailable, maybe, injured, away, busy, free
        - Personal references: my, me, myself, I, my info
        - Contact information: phone numbers, emails
        - Actions: update, change, modify, set, register, add
        - Match-related: fixture, game, training, practice

        EXTRACTION REQUIREMENTS:
        1. Identify all relevant entities with their categories
        2. Note the context each entity appears in
        3. Flag any ambiguous references that need clarification
        4. Consider football-specific meanings (e.g., "striker" as position vs action)

        Return the entities you find in JSON format with categories and context.
        """


@dataclass
class ConversationContextTemplate(FootballContextTemplate):
    """Template for conversation context analysis."""

    name: str = "conversation_context"
    description: str = "Analyze conversation context for multi-turn interactions"

    def get_context_model(self) -> type[BaseModel]:
        return PromptContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        Analyze the conversation context for user $username in $chat_type chat:

        USER: $username (ID: $telegram_id)
        TEAM: $team_id
        CHAT: $chat_type

        CONTEXT ANALYSIS REQUIREMENTS:
        1. Determine the user's likely role in the team based on chat context
        2. Assess appropriate response tone for this chat context
        3. Identify common follow-up questions this user might have
        4. Consider relevant team management context
        5. Note any permissions or restrictions that apply

        CHAT TYPE CONSIDERATIONS:
        - main: General team communication, player-focused operations
        - leadership: Administrative operations, team management
        - private: Personal queries, individual player information

        ROLE INFERENCE:
        - main chat users: Likely players or general team members
        - leadership chat users: Likely coaches, admins, or team leadership
        - private chat users: Could be any role, focus on personal context

        Provide conversation context insights in JSON format.
        """


@dataclass
class SemanticSimilarityTemplate(FootballContextTemplate):
    """Template for semantic similarity analysis."""

    name: str = "semantic_similarity"
    description: str = "Analyze semantic similarity between messages and commands"

    def get_context_model(self) -> type[BaseModel]:
        return SimilarityAnalysisContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        Analyze semantic similarity between this user message and available commands:

        USER MESSAGE: "$message"
        AVAILABLE COMMANDS: $reference_commands
        CONTEXT: $chat_type chat

        SIMILARITY ANALYSIS REQUIREMENTS:
        1. Identify commands most semantically similar to the user's intent
        2. Provide confidence scores for the top 3 matches (0.0-1.0)
        3. Determine if the user might be trying to use a specific command
        4. Suggest what the user might actually want to accomplish
        5. Consider football-specific terminology and context

        ANALYSIS APPROACH:
        - Focus on intent and meaning, not just word matching
        - Consider synonyms and football terminology
        - Account for common misspellings or variations
        - Understand context-dependent meanings

        COMMAND CATEGORIES:
        - Information: /info, /status, /list, /myinfo
        - Actions: /update, /register, /approve, /addplayer
        - Management: /matches, /availability, /attendance
        - Help: /help, /commands
        - System: /ping, /version

        Return similarity analysis in JSON format with recommendations.
        """


@dataclass
class RoutingRecommendationTemplate(FootballContextTemplate):
    """Template for intelligent routing recommendations."""

    name: str = "routing_recommendation"
    description: str = "Provide intelligent agent routing based on intent analysis"

    def get_context_model(self) -> type[BaseModel]:
        return RoutingContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        Analyze this intent data and recommend the best agent for routing:

        INTENT DATA: $intent_data
        CHAT CONTEXT: $chat_type
        USER: $username
        TEAM: $team_id

        AVAILABLE AGENTS:
        - message_processor: General communication, basic operations, system commands
        - help_assistant: Help system, guidance, command discovery, onboarding
        - player_coordinator: Player management, registration, status queries, approvals
        - team_administrator: Team member management, administrative operations (leadership only)
        - squad_selector: Match management, availability tracking, squad selection

        ROUTING CONSIDERATIONS:
        1. User's intent and what they're trying to accomplish
        2. Chat context permissions (main/leadership/private)
        3. Which agent has the appropriate tools and permissions
        4. Priority level based on urgency and importance
        5. Agent specialization and expertise areas

        PERMISSION MATRIX:
        - main chat: Player operations, general queries, availability
        - leadership chat: All operations including team administration
        - private chat: Personal operations, help, basic queries

        AGENT SPECIALIZATIONS:
        - message_processor: Fallback, communications, basic system operations
        - help_assistant: User guidance, command help, system explanation
        - player_coordinator: Player-centric operations, registration workflows
        - team_administrator: Leadership-only operations, member management
        - squad_selector: Match and squad management, availability coordination

        Recommend the optimal agent with clear reasoning in JSON format.
        """


@dataclass
class UpdateContextTemplate(FootballContextTemplate):
    """Template for update command context analysis."""

    name: str = "update_context"
    description: str = "Analyze update commands for intelligent routing"

    def get_context_model(self) -> type[BaseModel]:
        return UpdateAnalysisContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        Analyze this update command to determine the target and appropriate routing:

        UPDATE MESSAGE: "$message"
        CHAT CONTEXT: $chat_type
        USER: $username
        TEAM: $team_id

        UPDATE ANALYSIS REQUIREMENTS:
        1. What is being updated (player info, team member info, availability, etc.)
        2. Target entity type: "player" or "team_member"
        3. Recommended agent: player_coordinator or team_administrator
        4. Confidence level for this routing decision (0.0-1.0)
        5. Clear reasoning based on context and message content

        ROUTING LOGIC:
        - Main chat typically = player operations → player_coordinator
        - Leadership chat typically = team member operations → team_administrator
        - Message content provides additional context clues
        - Consider what makes most sense given the user's likely intent

        UPDATE TYPES:
        - Player updates: position, availability, contact info, status
        - Team member updates: role, permissions, administrative info
        - System updates: preferences, settings, configurations

        CONTEXT CLUES:
        - "my" updates usually target the requesting user's record
        - Specific names/phones usually target other users
        - Administrative language suggests team member operations
        - Player-specific terms suggest player operations

        Return update context analysis in JSON format.
        """


@dataclass
class PermissionValidationTemplate(FootballContextTemplate):
    """Template for permission validation prompts."""

    name: str = "permission_validation"
    description: str = "Validate permissions for routing decisions"

    def get_context_model(self) -> type[BaseModel]:
        return PermissionValidationContext

    def get_template(self) -> str:
        return f"""
        {self.get_base_context()}

        Validate permissions for this routing decision:

        USER: $username (Role: $user_role)
        CHAT CONTEXT: $chat_type
        REQUESTED ACTION: $requested_action
        TEAM: $team_id

        PERMISSION RULES:
        - Main chat: Player operations (status, availability, personal info)
        - Leadership chat: Team administration (add members, manage roles)
        - Private chat: Personal operations only

        ROLE HIERARCHY:
        - public: Basic access, limited operations
        - player: Player operations, own info management
        - team_member: Team member operations, enhanced access
        - leadership: Administrative operations, team management
        - admin: Full administrative access, all operations

        VALIDATION REQUIREMENTS:
        1. Is this action allowed for this user role?
        2. Is this chat context appropriate for this action?
        3. Should routing proceed or be blocked?
        4. What alternatives exist if the action is blocked?
        5. Clear reasoning for the permission decision

        COMMON RESTRICTIONS:
        - Team administration requires leadership chat + appropriate role
        - Player registration may require approval workflows
        - Cross-user operations need elevated permissions
        - Sensitive operations restricted to private/leadership chats

        Return permission validation results in JSON format.
        """


# =============================================================================
# Template Registry and Factory
# =============================================================================


class PromptTemplateRegistry:
    """
    Registry for managing prompt templates.
    Provides centralized access and caching.
    """

    def __init__(self):
        self._templates: dict[str, BasePromptTemplate] = {}
        self._register_default_templates()

    def _register_default_templates(self):
        """Register all default prompt templates."""
        templates = [
            IntentRecognitionTemplate(),
            EntityExtractionTemplate(),
            ConversationContextTemplate(),
            SemanticSimilarityTemplate(),
            RoutingRecommendationTemplate(),
            UpdateContextTemplate(),
            PermissionValidationTemplate(),
        ]

        for template in templates:
            self._templates[template.name] = template

    def get_template(self, name: str) -> BasePromptTemplate:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            Template instance

        Raises:
            KeyError: If template not found
        """
        if name not in self._templates:
            raise KeyError(
                f"Template '{name}' not found. Available: {list(self._templates.keys())}"
            )

        return self._templates[name]

    def register_template(self, template: BasePromptTemplate):
        """Register a new template."""
        self._templates[template.name] = template

    def list_templates(self) -> list[str]:
        """List all available template names."""
        return list(self._templates.keys())


# =============================================================================
# Global Registry Instance
# =============================================================================


@lru_cache(maxsize=1)
def get_prompt_registry() -> PromptTemplateRegistry:
    """
    Get the global prompt template registry.
    Cached for performance.
    """
    return PromptTemplateRegistry()


# =============================================================================
# Convenience Functions
# =============================================================================


def render_prompt(template_name: str, context: dict[str, Any]) -> str:
    """
    Convenience function to render a prompt by name.

    Args:
        template_name: Name of the template to use
        context: Context variables for the template

    Returns:
        Rendered prompt string

    Raises:
        KeyError: If template not found
        ValueError: If context validation fails
    """
    registry = get_prompt_registry()
    template = registry.get_template(template_name)
    return template.render(context)


def validate_prompt_context(template_name: str, context: dict[str, Any]) -> bool:
    """
    Validate context for a specific template without rendering.

    Args:
        template_name: Name of the template
        context: Context to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        registry = get_prompt_registry()
        template = registry.get_template(template_name)
        context_model = template.get_context_model()
        context_model(**context)
        return True
    except Exception as e:
        logger.debug(f"Context validation failed for {template_name}: {e}")
        return False
