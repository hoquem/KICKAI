#!/usr/bin/env python3
"""
Complexity Assessment Configuration

This module contains configuration data for complexity assessment, moving hardcoded
values out of the code to make the system more maintainable and configurable.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ComplexityFactors:
    """Configuration for complexity assessment factors."""
    
    # Intent complexity mappings
    simple_intents: List[str]
    moderate_intents: List[str]
    complex_intents: List[str]
    very_complex_intents: List[str]
    
    # Entity complexity mappings
    simple_entities: List[str]
    moderate_entities: List[str]
    complex_entities: List[str]
    
    # Context complexity indicators
    simple_context: List[str]
    moderate_context: List[str]
    complex_context: List[str]
    
    # Dependency complexity weights
    no_dependencies: float
    single_dependency: float
    multiple_dependencies: float
    circular_dependencies: float


@dataclass
class ComplexityWeights:
    """Configuration for complexity assessment weights."""
    
    intent: float
    entities: float
    context: float
    dependencies: float
    user_history: float


@dataclass
class ComplexityThresholds:
    """Configuration for complexity level thresholds."""
    
    simple_threshold: float
    moderate_threshold: float
    complex_threshold: float
    very_complex_threshold: float


@dataclass
class ProcessingTimeConfig:
    """Configuration for processing time estimation."""
    
    base_times: Dict[str, int]
    entity_complexity_threshold: float
    entity_complexity_adjustment: int
    dependency_complexity_threshold: float
    dependency_complexity_adjustment: int
    context_complexity_threshold: float
    context_complexity_adjustment: int


class ComplexityConfig:
    """Main configuration class for complexity assessment."""
    
    def __init__(self):
        self.factors = self._load_complexity_factors()
        self.weights = self._load_complexity_weights()
        self.thresholds = self._load_complexity_thresholds()
        self.processing_times = self._load_processing_time_config()
    
    def _load_complexity_factors(self) -> ComplexityFactors:
        """Load complexity assessment factors."""
        return ComplexityFactors(
            simple_intents=['status_inquiry', 'help_request', 'general_inquiry'],
            moderate_intents=['player_registration', 'payment_inquiry', 'match_inquiry'],
            complex_intents=['player_approval', 'availability_update'],
            very_complex_intents=['multi_step_operation', 'coordination_task'],
            
            simple_entities=['player_id', 'status'],
            moderate_entities=['player_name', 'phone', 'amount'],
            complex_entities=['match_details', 'payment_details', 'availability_schedule'],
            
            simple_context=['single_user', 'single_team'],
            moderate_context=['multiple_users', 'time_constraints'],
            complex_context=['multi_team', 'conflicting_requirements', 'urgent_deadlines'],
            
            no_dependencies=0.1,
            single_dependency=0.3,
            multiple_dependencies=0.6,
            circular_dependencies=0.9
        )
    
    def _load_complexity_weights(self) -> ComplexityWeights:
        """Load complexity assessment weights."""
        return ComplexityWeights(
            intent=0.3,
            entities=0.2,
            context=0.2,
            dependencies=0.15,
            user_history=0.15
        )
    
    def _load_complexity_thresholds(self) -> ComplexityThresholds:
        """Load complexity level thresholds."""
        return ComplexityThresholds(
            simple_threshold=0.3,
            moderate_threshold=0.6,
            complex_threshold=0.8,
            very_complex_threshold=1.0
        )
    
    def _load_processing_time_config(self) -> ProcessingTimeConfig:
        """Load processing time configuration."""
        return ProcessingTimeConfig(
            base_times={
                'SIMPLE': 15,
                'MODERATE': 45,
                'COMPLEX': 120,
                'VERY_COMPLEX': 300
            },
            entity_complexity_threshold=0.6,
            entity_complexity_adjustment=30,
            dependency_complexity_threshold=0.5,
            dependency_complexity_adjustment=60,
            context_complexity_threshold=0.7,
            context_complexity_adjustment=45
        )
    
    def get_intent_complexity_score(self, intent: str) -> float:
        """Get complexity score for an intent."""
        if intent in self.factors.simple_intents:
            return 0.2
        elif intent in self.factors.moderate_intents:
            return 0.4
        elif intent in self.factors.complex_intents:
            return 0.7
        elif intent in self.factors.very_complex_intents:
            return 0.9
        else:
            return 0.5  # Default moderate complexity
    
    def get_entity_complexity_score(self, entities: Dict[str, Any]) -> float:
        """Get complexity score for entities."""
        if not entities:
            return 0.1  # No entities = simple
        
        entity_scores = []
        
        for entity_type in entities.keys():
            if entity_type in self.factors.simple_entities:
                entity_scores.append(0.2)
            elif entity_type in self.factors.moderate_entities:
                entity_scores.append(0.4)
            elif entity_type in self.factors.complex_entities:
                entity_scores.append(0.7)
            else:
                entity_scores.append(0.5)  # Default
        
        # Return average entity complexity
        return sum(entity_scores) / len(entity_scores) if entity_scores else 0.1
    
    def get_context_complexity_score(self, context: Dict[str, Any]) -> float:
        """Get complexity score for context."""
        if not context:
            return 0.1  # No context = simple
        
        context_score = 0.1  # Base score
        
        # Check for complexity indicators
        if context.get('multiple_users', False):
            context_score += 0.3
        if context.get('time_constraints', False):
            context_score += 0.2
        if context.get('multi_team', False):
            context_score += 0.4
        if context.get('conflicting_requirements', False):
            context_score += 0.5
        if context.get('urgent_deadlines', False):
            context_score += 0.3
        
        return min(1.0, context_score)
    
    def get_dependency_complexity_score(self, dependencies: List[str]) -> float:
        """Get complexity score for dependencies."""
        if not dependencies:
            return self.factors.no_dependencies
        
        dependency_count = len(dependencies)
        
        if dependency_count == 1:
            return self.factors.single_dependency
        elif dependency_count <= 3:
            return self.factors.multiple_dependencies
        else:
            return self.factors.circular_dependencies
    
    def calculate_overall_complexity(self, factors: Dict[str, float]) -> tuple[float, str]:
        """Calculate overall complexity score and level."""
        overall_score = 0.0
        for factor, weight in self.weights.__dict__.items():
            if factor in factors:
                overall_score += factors[factor] * weight
        
        # Map score to complexity level
        if overall_score < self.thresholds.simple_threshold:
            complexity_level = 'SIMPLE'
        elif overall_score < self.thresholds.moderate_threshold:
            complexity_level = 'MODERATE'
        elif overall_score < self.thresholds.complex_threshold:
            complexity_level = 'COMPLEX'
        else:
            complexity_level = 'VERY_COMPLEX'
        
        return overall_score, complexity_level
    
    def estimate_processing_time(self, complexity_level: str, factors: Dict[str, float]) -> int:
        """Estimate processing time based on complexity."""
        base_time = self.processing_times.base_times.get(complexity_level, 60)
        adjustments = 0
        
        # Entity complexity adjustment
        if factors.get('entities', 0) > self.processing_times.entity_complexity_threshold:
            adjustments += self.processing_times.entity_complexity_adjustment
        
        # Dependency complexity adjustment
        if factors.get('dependencies', 0) > self.processing_times.dependency_complexity_threshold:
            adjustments += self.processing_times.dependency_complexity_adjustment
        
        # Context complexity adjustment
        if factors.get('context', 0) > self.processing_times.context_complexity_threshold:
            adjustments += self.processing_times.context_complexity_adjustment
        
        return base_time + adjustments
    
    def recommend_approach(self, complexity_level: str) -> str:
        """Recommend processing approach based on complexity."""
        if complexity_level == 'SIMPLE':
            return 'direct'
        elif complexity_level == 'MODERATE':
            return 'decomposed'
        else:  # COMPLEX or VERY_COMPLEX
            return 'collaborative'


# Global configuration instance
_complexity_config: ComplexityConfig = None


def get_complexity_config() -> ComplexityConfig:
    """Get the global complexity configuration instance."""
    global _complexity_config
    if _complexity_config is None:
        _complexity_config = ComplexityConfig()
    return _complexity_config 