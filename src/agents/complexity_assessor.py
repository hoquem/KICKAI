#!/usr/bin/env python3
"""
Simplified Request Complexity Assessor

This module provides a simplified, maintainable complexity assessment system
that uses external configuration and follows the single responsibility principle.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from config.complexity_config import get_complexity_config

logger = logging.getLogger(__name__)


@dataclass
class ComplexityAssessment:
    """Result of complexity assessment."""
    complexity_level: str
    score: float  # 0.0 to 1.0
    factors: dict[str, float]  # Individual factor scores
    reasoning: str
    estimated_processing_time: int  # seconds
    recommended_approach: str  # 'direct', 'decomposed', 'collaborative'


class RequestComplexityAssessor:
    """Simplified complexity assessor that uses external configuration."""

    def __init__(self):
        self.config = get_complexity_config()
        self.assessment_history = []
        logger.info("RequestComplexityAssessor initialized with configuration")

    def assess(self, request: str, intent: str, entities: dict[str, Any],
               context: dict[str, Any], dependencies: list[str] = None,
               user_id: str = None, user_history: list[dict[str, Any]] = None) -> ComplexityAssessment:
        """Assess the complexity of a request using configuration-based scoring."""

        # Assess individual factors using configuration
        factors = {
            'intent': self.config.get_intent_complexity_score(intent),
            'entities': self.config.get_entity_complexity_score(entities),
            'context': self.config.get_context_complexity_score(context),
            'dependencies': self.config.get_dependency_complexity_score(dependencies or [])
        }

        # Add user history if available
        if user_id and user_history:
            factors['user_history'] = self._assess_user_history_complexity(user_id, user_history)
        else:
            factors['user_history'] = 0.3  # Default moderate complexity

        # Calculate overall complexity using configuration
        overall_score, complexity_level = self.config.calculate_overall_complexity(factors)

        # Generate reasoning
        reasoning = self._generate_reasoning(factors, complexity_level)

        # Estimate processing time using configuration
        estimated_time = self.config.estimate_processing_time(complexity_level, factors)

        # Recommend approach using configuration
        recommended_approach = self.config.recommend_approach(complexity_level)

        assessment = ComplexityAssessment(
            complexity_level=complexity_level,
            score=overall_score,
            factors=factors,
            reasoning=reasoning,
            estimated_processing_time=estimated_time,
            recommended_approach=recommended_approach
        )

        # Log assessment
        self._log_assessment(request, intent, complexity_level, overall_score, factors,
                           estimated_time, recommended_approach)

        logger.info(f"Complexity assessment: {complexity_level} (score: {overall_score:.2f}) - {reasoning}")

        return assessment

    def _assess_user_history_complexity(self, user_id: str, user_history: list[dict[str, Any]]) -> float:
        """Assess complexity based on user interaction history."""
        if not user_history:
            return 0.3  # New user = moderate complexity

        # Analyze recent interactions
        recent_interactions = user_history[-10:]  # Last 10 interactions

        # Check for patterns that might indicate complexity
        complexity_indicators = 0

        for interaction in recent_interactions:
            # Check for errors or retries
            if interaction.get('had_error', False):
                complexity_indicators += 1

            # Check for multi-step operations
            if interaction.get('steps_required', 1) > 1:
                complexity_indicators += 1

            # Check for long processing times
            if interaction.get('processing_time', 0) > 30:  # More than 30 seconds
                complexity_indicators += 1

        # Normalize by number of interactions
        if recent_interactions:
            complexity_score = complexity_indicators / len(recent_interactions)
        else:
            complexity_score = 0.3

        return min(1.0, complexity_score)

    def _generate_reasoning(self, factors: dict[str, float], complexity_level: str) -> str:
        """Generate reasoning for complexity assessment."""
        reasoning_parts = []

        # Add primary factors
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        primary_factor, primary_score = sorted_factors[0]

        if primary_score > 0.7:
            reasoning_parts.append(f"High complexity in {primary_factor} ({primary_score:.2f})")
        elif primary_score > 0.4:
            reasoning_parts.append(f"Moderate complexity in {primary_factor} ({primary_score:.2f})")
        else:
            reasoning_parts.append(f"Low complexity in {primary_factor} ({primary_score:.2f})")

        # Add secondary factors if significant
        for factor, score in sorted_factors[1:3]:  # Top 3 factors
            if score > 0.5:
                reasoning_parts.append(f"Significant {factor} complexity ({score:.2f})")

        # Add overall assessment
        reasoning_parts.append(f"Overall assessment: {complexity_level.lower()} request")

        return "; ".join(reasoning_parts)

    def _log_assessment(self, request: str, intent: str, complexity_level: str,
                       score: float, factors: dict[str, float], estimated_time: int,
                       recommended_approach: str):
        """Log assessment for analytics."""
        self.assessment_history.append({
            'timestamp': datetime.now(),
            'request': request,
            'intent': intent,
            'complexity_level': complexity_level,
            'score': score,
            'factors': factors,
            'estimated_time': estimated_time,
            'recommended_approach': recommended_approach
        })

    def get_assessment_analytics(self) -> dict[str, Any]:
        """Get analytics about complexity assessments."""
        if not self.assessment_history:
            return {}

        total_assessments = len(self.assessment_history)
        complexity_counts = {}
        approach_counts = {}
        avg_scores = {}
        avg_processing_times = {}

        for entry in self.assessment_history:
            complexity = entry['complexity_level']
            approach = entry['recommended_approach']
            score = entry['score']
            processing_time = entry['estimated_time']

            # Count complexity levels
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1

            # Count approaches
            approach_counts[approach] = approach_counts.get(approach, 0) + 1

            # Track scores by complexity
            if complexity not in avg_scores:
                avg_scores[complexity] = []
            avg_scores[complexity].append(score)

            # Track processing times by complexity
            if complexity not in avg_processing_times:
                avg_processing_times[complexity] = []
            avg_processing_times[complexity].append(processing_time)

        # Calculate averages
        for complexity in avg_scores:
            avg_scores[complexity] = sum(avg_scores[complexity]) / len(avg_scores[complexity])
            avg_processing_times[complexity] = sum(avg_processing_times[complexity]) / len(avg_processing_times[complexity])

        return {
            'total_assessments': total_assessments,
            'complexity_distribution': complexity_counts,
            'approach_distribution': approach_counts,
            'average_scores_by_complexity': avg_scores,
            'average_processing_times_by_complexity': avg_processing_times,
            'recent_assessments': self.assessment_history[-10:]  # Last 10
        }

    async def aassess(self, request: str, intent: str, entities: dict[str, Any],
                     context: dict[str, Any], dependencies: list[str] = None,
                     user_id: str = None, user_history: list[dict[str, Any]] = None) -> ComplexityAssessment:
        """Async assess complexity."""
        return self.assess(request, intent, entities, context, dependencies, user_id, user_history)
