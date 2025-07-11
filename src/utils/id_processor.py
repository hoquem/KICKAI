"""
Centralized ID Processing Service - Single Source of Truth

This module provides a centralized service for processing, validating, and normalizing
all types of IDs used in the KICKAI system (player IDs, team IDs, equipment IDs, etc.).

This follows the single source of truth principle - all ID processing logic should
go through this service to ensure consistency across the entire system.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class IDType(Enum):
    """Types of IDs that can be processed."""
    PLAYER_ID = "player_id"
    TEAM_ID = "team_id"
    EQUIPMENT_ID = "equipment_id"
    MATCH_ID = "match_id"
    PAYMENT_ID = "payment_id"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    USERNAME = "username"


@dataclass
class ProcessedID:
    """Result of ID processing."""
    id_type: IDType
    original_value: str
    normalized_value: str
    is_valid: bool
    confidence: float  # 0.0 to 1.0
    validation_errors: List[str]
    extracted_from: str  # Source text where ID was found
    extraction_method: str  # Method used to extract the ID


@dataclass
class EntityExtractionResult:
    """Result of entity extraction from text."""
    entities: Dict[str, ProcessedID]
    extraction_method: str
    confidence: float
    source_text: str
    processing_time_ms: float


class IDProcessor:
    """
    Centralized ID processing service - the single source of truth for all ID operations.
    
    This service handles:
    - ID extraction from text
    - ID validation and normalization
    - ID format conversion
    - Entity extraction for commands
    """
    
    def __init__(self):
        # Define ID patterns and validation rules
        self.id_patterns = {
            IDType.PLAYER_ID: {
                'pattern': r'\b[a-zA-Z]{2,4}\d*\b',
                'validation_rules': [
                    lambda x: len(x) >= 2 and len(x) <= 6,
                    lambda x: x[0].isalpha(),
                    lambda x: x.isalnum()
                ],
                'normalization': lambda x: x.upper().strip()
            },
            IDType.TEAM_ID: {
                'pattern': r'\b[A-Z]{2,4}\b',
                'validation_rules': [
                    lambda x: len(x) >= 2 and len(x) <= 4,
                    lambda x: x.isalpha(),
                    lambda x: x.isupper()
                ],
                'normalization': lambda x: x.upper().strip()
            },
            IDType.PHONE_NUMBER: {
                'pattern': r'\b(?:\+?44|0)?[17]\d{9}\b',
                'validation_rules': [
                    lambda x: len(x) >= 10 and len(x) <= 13,
                    lambda x: re.match(r'^[\d\+]+$', x)
                ],
                'normalization': self._normalize_phone_number
            },
            IDType.EMAIL: {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'validation_rules': [
                    lambda x: '@' in x,
                    lambda x: '.' in x.split('@')[1]
                ],
                'normalization': lambda x: x.lower().strip()
            },
            IDType.MATCH_ID: {
                'pattern': r'\bMATCH\d{3,6}\b',
                'validation_rules': [
                    lambda x: x.startswith('MATCH'),
                    lambda x: x[5:].isdigit()
                ],
                'normalization': lambda x: x.upper().strip()
            }
        }
        
        # Command-specific entity extraction patterns
        self.command_patterns = {
            '/approve': {
                'required_entities': [IDType.PLAYER_ID],
                'optional_entities': [],
                'extraction_method': 'command_parameter'
            },
            '/register': {
                'required_entities': [IDType.PLAYER_ID],
                'optional_entities': [IDType.PHONE_NUMBER, IDType.EMAIL],
                'extraction_method': 'command_parameter'
            },
            '/add': {
                'required_entities': [IDType.PHONE_NUMBER],
                'optional_entities': [IDType.PLAYER_ID],
                'extraction_method': 'command_parameter'
            },
            '/status': {
                'required_entities': [IDType.PHONE_NUMBER],
                'optional_entities': [IDType.PLAYER_ID],
                'extraction_method': 'command_parameter'
            },
            '/invitelink': {
                'description': 'Generate invitation link for a player',
                'usage': '/invitelink [phone_or_player_id]',
                'example': '/invitelink 07123456789'
            },
            '/addteam': {
                'description': 'Add a new team',
                'usage': '/addteam [name] [description]',
                'example': '/addteam "Team Alpha" "Sunday League Team"'
            },
            '/removeteam': {
                'description': 'Remove a team',
                'usage': '/removeteam [team_id]',
                'example': '/removeteam KAI'
            },
            '/listteams': {
                'description': 'List all teams',
                'usage': '/listteams [filter]',
                'example': '/listteams active'
            },
            '/updateteaminfo': {
                'description': 'Update team information',
                'usage': '/updateteaminfo [team_id] [field] [value]',
                'example': '/updateteaminfo KAI name "New Team Name"'
            },
            '/creatematch': {
                'description': 'Create a new match',
                'usage': '/creatematch [date] [time] [location] [opponent]',
                'example': '/creatematch 2024-06-15 14:00 "Local Park" "Team Beta"'
            },
            '/attendmatch': {
                'description': 'Mark attendance for a match',
                'usage': '/attendmatch [match_id] [availability]',
                'example': '/attendmatch MATCH001 yes'
            },
            '/unattendmatch': {
                'description': 'Cancel attendance for a match',
                'usage': '/unattendmatch [match_id]',
                'example': '/unattendmatch MATCH001'
            },
            '/listmatches': {
                'description': 'List matches',
                'usage': '/listmatches [filter]',
                'example': '/listmatches upcoming'
            },
            '/recordresult': {
                'description': 'Record match result',
                'usage': '/recordresult [match_id] [our_score] [their_score]',
                'example': '/recordresult MATCH001 3 1'
            },
            '/createpayment': {
                'description': 'Create a payment',
                'usage': '/createpayment [amount] [description] [player_id]',
                'example': '/createpayment 25.00 "Match fee" AB1'
            },
            '/paymentstatus': {
                'description': 'Check payment status',
                'usage': '/paymentstatus [payment_id/player_id]',
                'example': '/paymentstatus PAY001'
            },
            '/pendingpayments': {
                'description': 'List pending payments',
                'usage': '/pendingpayments [filter]',
                'example': '/pendingpayments overdue'
            },
            '/paymenthistory': {
                'description': 'Get payment history',
                'usage': '/paymenthistory [player_id] [period]',
                'example': '/paymenthistory AB1 month'
            },
            '/financialdashboard': {
                'description': 'Show financial dashboard',
                'usage': '/financialdashboard [period]',
                'example': '/financialdashboard month'
            },
            '/promoteuser': {
                'description': 'Promote a user',
                'usage': '/promoteuser [user_id] [role]',
                'example': '/promoteuser 123456789 admin'
            },
            '/demoteuser': {
                'description': 'Demote a user',
                'usage': '/demoteuser [user_id] [reason]',
                'example': '/demoteuser 123456789 "Inactive user"'
            },
            '/systemstatus': {
                'description': 'Show system status',
                'usage': '/systemstatus [detailed]',
                'example': '/systemstatus true'
            }
        }
    
    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number to international format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d\+]', '', phone)
        
        # Handle UK mobile numbers
        if cleaned.startswith('0'):
            cleaned = '+44' + cleaned[1:]
        elif cleaned.startswith('44'):
            cleaned = '+' + cleaned
        elif not cleaned.startswith('+'):
            cleaned = '+44' + cleaned
            
        return cleaned
    
    def extract_entities_from_text(self, text: str, expected_entities: Optional[List[IDType]] = None) -> EntityExtractionResult:
        """
        Extract entities from text using centralized logic.
        
        Args:
            text: Text to extract entities from
            expected_entities: List of expected entity types (if None, extract all)
            
        Returns:
            EntityExtractionResult with extracted entities
        """
        start_time = datetime.now()
        
        if not text or not text.strip():
            return EntityExtractionResult(
                entities={},
                extraction_method='empty_text',
                confidence=0.0,
                source_text=text,
                processing_time_ms=0.0
            )
        
        entities = {}
        extraction_methods = []
        
        # Extract all entity types if none specified
        entity_types = expected_entities or list(IDType)
        
        for entity_type in entity_types:
            if entity_type not in self.id_patterns:
                continue
                
            pattern_info = self.id_patterns[entity_type]
            pattern = pattern_info['pattern']
            
            # Find all matches
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Validate and normalize the match
                processed_id = self._process_id(match, entity_type, text)
                
                if processed_id.is_valid:
                    entity_key = entity_type.value
                    entities[entity_key] = processed_id
                    extraction_methods.append(f"{entity_type.value}_regex")
        
        # Calculate confidence based on extraction success
        confidence = min(1.0, len(entities) / max(1, len(entity_types)))
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EntityExtractionResult(
            entities=entities,
            extraction_method='_'.join(extraction_methods) if extraction_methods else 'none',
            confidence=confidence,
            source_text=text,
            processing_time_ms=processing_time
        )
    
    def extract_entities_from_command(self, command_text: str, command_name: str) -> EntityExtractionResult:
        """
        Extract entities from a specific command using command-specific patterns.
        
        Args:
            command_text: Full command text (e.g., "/approve AB")
            command_name: Command name (e.g., "/approve")
            
        Returns:
            EntityExtractionResult with extracted entities
        """
        if command_name not in self.command_patterns:
            # Fallback to general entity extraction
            return self.extract_entities_from_text(command_text)
        
        command_info = self.command_patterns[command_name]
        required_entities = command_info['required_entities']
        optional_entities = command_info['optional_entities']
        
        # Extract entities using command-specific logic
        entities = {}
        extraction_methods = []
        
        # For command parameters, extract from the command arguments
        if command_info['extraction_method'] == 'command_parameter':
            # Split command into parts
            parts = command_text.split()
            if len(parts) > 1:
                # Extract from the first argument (after command name)
                argument = parts[1]
                
                # Try to match against required entities first
                for entity_type in required_entities + optional_entities:
                    if entity_type in self.id_patterns:
                        pattern = self.id_patterns[entity_type]['pattern']
                        if re.match(pattern, argument, re.IGNORECASE):
                            processed_id = self._process_id(argument, entity_type, command_text)
                            if processed_id.is_valid:
                                entities[entity_type.value] = processed_id
                                extraction_methods.append(f"{entity_type.value}_command_param")
                                break  # Use first match
        
        # If no entities found in command parameters, try general extraction
        if not entities:
            general_result = self.extract_entities_from_text(command_text, required_entities + optional_entities)
            entities = general_result.entities
            extraction_methods.append(general_result.extraction_method)
        
        # Calculate confidence
        confidence = min(1.0, len(entities) / max(1, len(required_entities)))
        
        return EntityExtractionResult(
            entities=entities,
            extraction_method='_'.join(extraction_methods) if extraction_methods else 'none',
            confidence=confidence,
            source_text=command_text,
            processing_time_ms=0.0
        )
    
    def _process_id(self, value: str, id_type: IDType, source_text: str) -> ProcessedID:
        """
        Process and validate a single ID value.
        
        Args:
            value: The ID value to process
            id_type: Type of ID being processed
            source_text: Source text where ID was found
            
        Returns:
            ProcessedID with validation results
        """
        if id_type not in self.id_patterns:
            return ProcessedID(
                id_type=id_type,
                original_value=value,
                normalized_value=value,
                is_valid=False,
                confidence=0.0,
                validation_errors=[f"Unknown ID type: {id_type}"],
                extracted_from=source_text,
                extraction_method='unknown_type'
            )
        
        pattern_info = self.id_patterns[id_type]
        validation_errors = []
        
        # Normalize the value
        try:
            normalized_value = pattern_info['normalization'](value)
        except Exception as e:
            normalized_value = value
            validation_errors.append(f"Normalization failed: {str(e)}")
        
        # Validate using rules
        for rule in pattern_info['validation_rules']:
            try:
                if not rule(normalized_value):
                    validation_errors.append(f"Failed validation rule: {rule.__name__ if hasattr(rule, '__name__') else 'unknown'}")
            except Exception as e:
                validation_errors.append(f"Validation rule error: {str(e)}")
        
        # Calculate confidence based on validation success
        confidence = 1.0 - (len(validation_errors) / len(pattern_info['validation_rules']))
        
        return ProcessedID(
            id_type=id_type,
            original_value=value,
            normalized_value=normalized_value,
            is_valid=len(validation_errors) == 0,
            confidence=confidence,
            validation_errors=validation_errors,
            extracted_from=source_text,
            extraction_method='pattern_match'
        )
    
    def validate_id(self, value: str, id_type: IDType) -> Tuple[bool, List[str]]:
        """
        Validate an ID value.
        
        Args:
            value: ID value to validate
            id_type: Type of ID to validate
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        processed_id = self._process_id(value, id_type, "validation")
        return processed_id.is_valid, processed_id.validation_errors
    
    def normalize_id(self, value: str, id_type: IDType) -> str:
        """
        Normalize an ID value.
        
        Args:
            value: ID value to normalize
            id_type: Type of ID to normalize
            
        Returns:
            Normalized ID value
        """
        processed_id = self._process_id(value, id_type, "normalization")
        return processed_id.normalized_value
    
    def get_entity_value(self, entities: Dict[str, ProcessedID], entity_name: str) -> Optional[str]:
        """
        Get the normalized value of an entity from the entities dictionary.
        
        Args:
            entities: Dictionary of extracted entities
            entity_name: Name of the entity to get
            
        Returns:
            Normalized entity value or None if not found
        """
        if entity_name in entities and entities[entity_name].is_valid:
            return entities[entity_name].normalized_value
        return None


# Global instance - single source of truth
_id_processor: Optional[IDProcessor] = None


def get_id_processor() -> IDProcessor:
    """Get the global ID processor instance."""
    global _id_processor
    if _id_processor is None:
        _id_processor = IDProcessor()
    return _id_processor


def extract_entities_from_text(text: str, expected_entities: Optional[List[IDType]] = None) -> EntityExtractionResult:
    """Convenience function to extract entities from text."""
    return get_id_processor().extract_entities_from_text(text, expected_entities)


def extract_entities_from_command(command_text: str, command_name: str) -> EntityExtractionResult:
    """Convenience function to extract entities from a command."""
    return get_id_processor().extract_entities_from_command(command_text, command_name)


def validate_id(value: str, id_type: IDType) -> Tuple[bool, List[str]]:
    """Convenience function to validate an ID."""
    return get_id_processor().validate_id(value, id_type)


def normalize_id(value: str, id_type: IDType) -> str:
    """Convenience function to normalize an ID."""
    return get_id_processor().normalize_id(value, id_type) 