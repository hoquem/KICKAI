#!/usr/bin/env python3
"""
Intelligent System - Intent Classification and Orchestration

This module provides intent classification and intelligent routing for the CrewAI system.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents."""
    PLAYER_REGISTRATION = "player_registration"
    TEAM_MANAGEMENT = "team_management"
    MATCH_MANAGEMENT = "match_management"
    PAYMENT_MANAGEMENT = "payment_management"
    ATTENDANCE_MANAGEMENT = "attendance_management"
    INFORMATION_QUERY = "information_query"
    HELP_REQUEST = "help_request"
    GREETING = "greeting"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: IntentType
    confidence: float  # 0.0 to 1.0
    entities: Dict[str, Any]
    reasoning: str


class IntentClassifier:
    """Simple rule-based intent classifier."""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.intent_patterns = self._build_intent_patterns()
        logger.info("IntentClassifier initialized")
    
    def _build_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Build patterns for intent classification."""
        return {
            IntentType.PLAYER_REGISTRATION: [
                "register", "add player", "new player", "join team", "sign up",
                "player registration", "add member", "new member"
            ],
            IntentType.TEAM_MANAGEMENT: [
                "team", "admin", "management", "leadership", "approve", "reject",
                "team member", "admin command"
            ],
            IntentType.MATCH_MANAGEMENT: [
                "match", "game", "fixture", "schedule", "organize", "arrange",
                "match day", "game day"
            ],
            IntentType.PAYMENT_MANAGEMENT: [
                "payment", "pay", "money", "fee", "subscription", "budget",
                "expense", "cost"
            ],
            IntentType.ATTENDANCE_MANAGEMENT: [
                "attendance", "available", "unavailable", "coming", "not coming",
                "confirm", "cancel", "status"
            ],
            IntentType.INFORMATION_QUERY: [
                "info", "information", "details", "check", "status", "list",
                "show", "what", "how", "when", "where"
            ],
            IntentType.HELP_REQUEST: [
                "help", "assist", "support", "guide", "how to", "what can",
                "commands", "options"
            ],
            IntentType.GREETING: [
                "hello", "hi", "hey", "good morning", "good afternoon",
                "good evening", "greetings"
            ]
        }
    
    def classify(self, text: str, context: Dict[str, Any] = None) -> IntentResult:
        """
        Classify the intent of a text message.
        
        Args:
            text: The text message to classify
            context: Additional context information
            
        Returns:
            IntentResult with classified intent and confidence
        """
        try:
            text_lower = text.lower().strip()
            
            # Check for exact command matches first
            if text_lower.startswith('/'):
                return self._classify_command(text_lower)
            
            # Check for pattern matches
            best_intent = IntentType.UNKNOWN
            best_confidence = 0.0
            best_reasoning = "No patterns matched"
            
            for intent_type, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        confidence = len(pattern) / len(text_lower)  # Simple confidence scoring
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_intent = intent_type
                            best_reasoning = f"Matched pattern: '{pattern}'"
            
            # Extract entities based on intent
            entities = self._extract_entities(text_lower, best_intent, context)
            
            # Boost confidence for certain patterns
            if best_intent != IntentType.UNKNOWN:
                best_confidence = min(1.0, best_confidence + 0.3)  # Boost confidence
            
            return IntentResult(
                intent=best_intent,
                confidence=best_confidence,
                entities=entities,
                reasoning=best_reasoning
            )
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                entities={},
                reasoning=f"Error during classification: {str(e)}"
            )
    
    def _classify_command(self, text: str) -> IntentResult:
        """Classify slash commands using the command registry as single source of truth."""
        try:
            from core.command_registry import get_command_registry
            
            # Get command from registry
            registry = get_command_registry()
            command_metadata = registry.get_command(text)
            
            if command_metadata:
                # Map command type to intent type
                intent_mapping = {
                    'player_registration': IntentType.PLAYER_REGISTRATION,
                    'team_management': IntentType.TEAM_MANAGEMENT,
                    'match_management': IntentType.MATCH_MANAGEMENT,
                    'payment_management': IntentType.PAYMENT_MANAGEMENT,
                    'attendance_management': IntentType.ATTENDANCE_MANAGEMENT,
                    'communication': IntentType.HELP_REQUEST,  # Help/start commands
                }
                
                intent_type = intent_mapping.get(command_metadata.feature, IntentType.INFORMATION_QUERY)
                
                return IntentResult(
                    intent=intent_type,
                    confidence=1.0,
                    entities={
                        'command_name': command_metadata.name,
                        'feature': command_metadata.feature,
                        'permission_level': command_metadata.permission_level.value
                    },
                    reasoning=f"Command from registry: {command_metadata.name}"
                )
            
            # Fallback for unregistered commands
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                entities={'command_name': text, 'feature': 'unknown', 'permission_level': 'public'},
                reasoning="Command not found in registry"
            )
            
        except Exception as e:
            logger.error(f"Error classifying command {text}: {e}")
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                entities={'command_name': text, 'feature': 'unknown', 'permission_level': 'public'},
                reasoning=f"Error during command classification: {str(e)}"
            )
    
    def _extract_entities(self, text: str, intent: IntentType, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract entities from text based on intent."""
        entities = {}
        
        if intent == IntentType.PLAYER_REGISTRATION:
            # Extract name, phone, position from text
            words = text.split()
            for i, word in enumerate(words):
                if word.startswith('+') or word.startswith('0'):
                    entities['phone'] = word
                    # Name is everything before phone
                    if i > 0:
                        entities['name'] = ' '.join(words[:i])
                    # Position is everything after phone
                    if i < len(words) - 1:
                        entities['position'] = ' '.join(words[i+1:])
                    break
        
        elif intent == IntentType.TEAM_MANAGEMENT:
            # Extract role, name, phone
            words = text.split()
            for i, word in enumerate(words):
                if word.startswith('+') or word.startswith('0'):
                    entities['phone'] = word
                    if i > 0:
                        entities['name'] = ' '.join(words[:i])
                    if i < len(words) - 1:
                        entities['role'] = ' '.join(words[i+1:])
                    break
        
        # Add context entities
        if context:
            entities.update(context)
        
        return entities 