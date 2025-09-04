#!/usr/bin/env python3
"""
KICKAI Prompt Template System

This package provides a centralized, type-safe prompt management system for
the NLP Processor agent and other components that need structured prompt generation.

Key Features:
- Template inheritance and composition
- Type-safe parameter validation with Pydantic
- Centralized prompt library with versioning
- Performance optimization with caching
- Football-specific context and terminology

Usage:
    from kickai.agents.prompts import render_prompt, get_prompt_registry

    # Render a prompt
    context = {
        'telegram_id': 123456789,
        'team_id': 'KTI',
        'username': 'player1',
        'chat_type': 'main',
        'message': 'What is my status?'
    }

    prompt = render_prompt('intent_recognition', context)

    # Get template registry for advanced usage
    registry = get_prompt_registry()
    template = registry.get_template('entity_extraction')
"""

from kickai.agents.prompts.nlp_prompts import (
    # Core classes
    BasePromptTemplate,
    ConversationContextTemplate,
    EntityExtractionContext,
    EntityExtractionTemplate,
    FootballContextTemplate,
    IntentAnalysisContext,
    # Template implementations
    IntentRecognitionTemplate,
    PermissionValidationContext,
    PermissionValidationTemplate,
    # Context models
    PromptContext,
    PromptTemplateRegistry,
    RoutingContext,
    RoutingRecommendationTemplate,
    SemanticSimilarityTemplate,
    SimilarityAnalysisContext,
    UpdateAnalysisContext,
    UpdateContextTemplate,
    # Registry and convenience functions
    get_prompt_registry,
    render_prompt,
    validate_prompt_context,
)

__all__ = [
    # Core classes
    "BasePromptTemplate",
    "FootballContextTemplate",
    "PromptTemplateRegistry",
    # Context models
    "PromptContext",
    "IntentAnalysisContext",
    "EntityExtractionContext",
    "RoutingContext",
    "UpdateAnalysisContext",
    "PermissionValidationContext",
    "SimilarityAnalysisContext",
    # Template implementations
    "IntentRecognitionTemplate",
    "EntityExtractionTemplate",
    "ConversationContextTemplate",
    "SemanticSimilarityTemplate",
    "RoutingRecommendationTemplate",
    "UpdateContextTemplate",
    "PermissionValidationTemplate",
    # Registry and convenience functions
    "get_prompt_registry",
    "render_prompt",
    "validate_prompt_context",
]
