#!/usr/bin/env python3
"""
Learning Tools for KICKAI
Specialized tools for the Learning Agent to improve natural language processing and system performance.
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)

@dataclass
class InteractionPattern:
    """Represents a learned interaction pattern."""
    pattern_type: str
    trigger_conditions: List[str]
    response_pattern: str
    success_rate: float
    usage_count: int
    last_used: datetime
    confidence: float

@dataclass
class UserPreference:
    """Represents a learned user preference."""
    user_id: str
    preference_type: str
    value: str
    confidence: float
    last_updated: datetime
    usage_count: int

class LearningTools(BaseTool):
    """Tools for the Learning Agent to analyze and improve system performance."""
    
    name = "Learning Tools"
    description = "Tools for learning from interactions and improving natural language processing"
    
    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.interaction_patterns = {}
        self.user_preferences = {}
        self.performance_metrics = {}
        
    def _run(self, command: str, **kwargs) -> str:
        """Execute learning tool commands."""
        try:
            if command == "analyze_interaction":
                return self._analyze_interaction(**kwargs)
            elif command == "learn_pattern":
                return self._learn_pattern(**kwargs)
            elif command == "get_user_preferences":
                return self._get_user_preferences(**kwargs)
            elif command == "update_user_preference":
                return self._update_user_preference(**kwargs)
            elif command == "analyze_natural_language":
                return self._analyze_natural_language(**kwargs)
            elif command == "optimize_response":
                return self._optimize_response(**kwargs)
            elif command == "get_learning_insights":
                return self._get_learning_insights(**kwargs)
            elif command == "suggest_improvements":
                return self._suggest_improvements(**kwargs)
            else:
                return f"Unknown learning command: {command}"
        except Exception as e:
            logger.error(f"Error in learning tool: {e}")
            return f"Error: {str(e)}"
    
    def _analyze_interaction(self, message: str, response: str, user_id: str, success: bool, **kwargs) -> str:
        """Analyze an interaction to extract learning insights."""
        try:
            analysis = {
                'message_length': len(message),
                'response_length': len(response),
                'success': success,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'message_complexity': self._calculate_complexity(message),
                'response_quality': self._assess_response_quality(response),
                'intent_identified': self._identify_intent(message),
                'entities_extracted': self._extract_entities(message)
            }
            
            # Store analysis for pattern learning
            self._store_interaction_analysis(analysis)
            
            return json.dumps(analysis, indent=2)
        except Exception as e:
            return f"Error analyzing interaction: {str(e)}"
    
    def _learn_pattern(self, pattern_type: str, trigger_conditions: List[str], 
                      response_pattern: str, success: bool, **kwargs) -> str:
        """Learn a new interaction pattern."""
        try:
            pattern_id = f"{pattern_type}_{len(self.interaction_patterns)}"
            
            pattern = InteractionPattern(
                pattern_type=pattern_type,
                trigger_conditions=trigger_conditions,
                response_pattern=response_pattern,
                success_rate=1.0 if success else 0.0,
                usage_count=1,
                last_used=datetime.now(),
                confidence=0.7
            )
            
            self.interaction_patterns[pattern_id] = pattern
            
            return f"Pattern learned: {pattern_id} (confidence: {pattern.confidence})"
        except Exception as e:
            return f"Error learning pattern: {str(e)}"
    
    def _get_user_preferences(self, user_id: str, **kwargs) -> str:
        """Get learned preferences for a user."""
        try:
            user_prefs = self.user_preferences.get(user_id, {})
            return json.dumps(user_prefs, indent=2, default=str)
        except Exception as e:
            return f"Error getting user preferences: {str(e)}"
    
    def _update_user_preference(self, user_id: str, preference_type: str, 
                               value: str, confidence: float = 0.7, **kwargs) -> str:
        """Update or create a user preference."""
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            preference = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                value=value,
                confidence=confidence,
                last_updated=datetime.now(),
                usage_count=1
            )
            
            self.user_preferences[user_id][preference_type] = preference
            
            return f"Preference updated: {preference_type} = {value} (confidence: {confidence})"
        except Exception as e:
            return f"Error updating user preference: {str(e)}"
    
    def _analyze_natural_language(self, message: str, **kwargs) -> str:
        """Analyze natural language for intent and entities."""
        try:
            analysis = {
                'intent': self._identify_intent(message),
                'entities': self._extract_entities(message),
                'complexity': self._calculate_complexity(message),
                'sentiment': self._analyze_sentiment(message),
                'suggested_improvements': self._suggest_nl_improvements(message)
            }
            
            return json.dumps(analysis, indent=2)
        except Exception as e:
            return f"Error analyzing natural language: {str(e)}"
    
    def _optimize_response(self, original_response: str, user_id: str, **kwargs) -> str:
        """Optimize a response based on learned user preferences."""
        try:
            user_prefs = self.user_preferences.get(user_id, {})
            
            # Apply user preferences
            optimized_response = original_response
            
            # Adjust response length based on preference
            length_pref = user_prefs.get('response_length', None)
            if length_pref:
                if length_pref.value == 'concise' and len(optimized_response) > 100:
                    optimized_response = self._make_concise(optimized_response)
                elif length_pref.value == 'detailed' and len(optimized_response) < 50:
                    optimized_response = self._add_detail(optimized_response)
            
            # Adjust communication style
            style_pref = user_prefs.get('communication_style', None)
            if style_pref:
                if style_pref.value == 'formal':
                    optimized_response = self._make_formal(optimized_response)
                elif style_pref.value == 'casual':
                    optimized_response = self._make_casual(optimized_response)
            
            return optimized_response
        except Exception as e:
            return f"Error optimizing response: {str(e)}"
    
    def _get_learning_insights(self, **kwargs) -> str:
        """Get insights from the learning system."""
        try:
            insights = {
                'total_patterns': len(self.interaction_patterns),
                'total_users': len(self.user_preferences),
                'top_patterns': self._get_top_patterns(),
                'user_insights': self._get_user_insights(),
                'performance_trends': self._get_performance_trends(),
                'recommendations': self._generate_recommendations()
            }
            
            return json.dumps(insights, indent=2)
        except Exception as e:
            return f"Error getting learning insights: {str(e)}"
    
    def _suggest_improvements(self, **kwargs) -> str:
        """Suggest system improvements based on learned patterns."""
        try:
            improvements = []
            
            # Analyze patterns for improvement opportunities
            for pattern_id, pattern in self.interaction_patterns.items():
                if pattern.success_rate < 0.7:
                    improvements.append(f"Low success pattern {pattern_id}: {pattern.pattern_type}")
                
                if pattern.usage_count > 10 and pattern.confidence < 0.8:
                    improvements.append(f"High usage, low confidence pattern {pattern_id}")
            
            # Analyze user preferences for gaps
            for user_id, prefs in self.user_preferences.items():
                if len(prefs) < 3:
                    improvements.append(f"User {user_id} has limited preference data")
            
            return json.dumps(improvements, indent=2)
        except Exception as e:
            return f"Error suggesting improvements: {str(e)}"
    
    # Helper methods
    def _calculate_complexity(self, message: str) -> float:
        """Calculate message complexity score."""
        base_score = 5.0
        
        # Length factor
        if len(message) > 100:
            base_score += 2
        elif len(message) < 20:
            base_score -= 1
        
        # Keyword complexity
        complex_keywords = ['plan', 'coordinate', 'analyze', 'manage', 'organize', 'strategy']
        if any(keyword in message.lower() for keyword in complex_keywords):
            base_score += 2
        
        return min(max(base_score, 1.0), 10.0)
    
    def _identify_intent(self, message: str) -> str:
        """Identify the intent of a message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['add', 'create', 'new']):
            return 'creation'
        elif any(word in message_lower for word in ['list', 'show', 'get', 'find']):
            return 'retrieval'
        elif any(word in message_lower for word in ['update', 'change', 'modify']):
            return 'modification'
        elif any(word in message_lower for word in ['delete', 'remove', 'cancel']):
            return 'deletion'
        elif any(word in message_lower for word in ['help', 'what', 'how']):
            return 'information'
        else:
            return 'general'
    
    def _extract_entities(self, message: str) -> List[str]:
        """Extract entities from a message."""
        entities = []
        
        # Extract names (simple pattern)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, message)
        entities.extend(names)
        
        # Extract phone numbers
        phone_pattern = r'\b07\d{9}\b'
        phones = re.findall(phone_pattern, message)
        entities.extend(phones)
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, message)
        entities.extend(dates)
        
        return entities
    
    def _assess_response_quality(self, response: str) -> float:
        """Assess the quality of a response."""
        quality_score = 5.0
        
        # Length factor
        if 50 <= len(response) <= 200:
            quality_score += 1
        elif len(response) < 20:
            quality_score -= 2
        
        # Clarity indicators
        if '✅' in response or 'successfully' in response.lower():
            quality_score += 1
        if '❌' in response or 'error' in response.lower():
            quality_score -= 1
        
        # Structure indicators
        if '\n' in response or '•' in response:
            quality_score += 1
        
        return min(max(quality_score, 1.0), 10.0)
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analyze sentiment of a message."""
        positive_words = ['good', 'great', 'excellent', 'thanks', 'thank you', 'please']
        negative_words = ['bad', 'terrible', 'error', 'wrong', 'fail', 'problem']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _suggest_nl_improvements(self, message: str) -> List[str]:
        """Suggest improvements for natural language processing."""
        suggestions = []
        
        if len(message) < 10:
            suggestions.append("Message is very short - consider asking for clarification")
        
        if not any(word in message.lower() for word in ['player', 'match', 'team', 'fixture']):
            suggestions.append("Message doesn't contain football-related keywords")
        
        if len(self._extract_entities(message)) == 0:
            suggestions.append("No clear entities identified - may need better parsing")
        
        return suggestions
    
    def _make_concise(self, response: str) -> str:
        """Make a response more concise."""
        # Simple implementation - take first sentence
        sentences = response.split('.')
        return sentences[0] + '.' if sentences else response
    
    def _add_detail(self, response: str) -> str:
        """Add more detail to a response."""
        return response + " Please let me know if you need any additional information."
    
    def _make_formal(self, response: str) -> str:
        """Make a response more formal."""
        return response.replace("!", ".").replace("😊", "").replace("👍", "")
    
    def _make_casual(self, response: str) -> str:
        """Make a response more casual."""
        return response.replace(".", "! 😊").replace("Thank you", "Thanks")
    
    def _get_top_patterns(self) -> List[Dict]:
        """Get top performing patterns."""
        sorted_patterns = sorted(
            self.interaction_patterns.items(),
            key=lambda x: (x[1].success_rate, x[1].usage_count),
            reverse=True
        )
        
        return [
            {
                'pattern_id': pattern_id,
                'type': pattern.pattern_type,
                'success_rate': pattern.success_rate,
                'usage_count': pattern.usage_count
            }
            for pattern_id, pattern in sorted_patterns[:5]
        ]
    
    def _get_user_insights(self) -> Dict:
        """Get insights about user behavior."""
        total_users = len(self.user_preferences)
        avg_preferences = sum(len(prefs) for prefs in self.user_preferences.values()) / total_users if total_users > 0 else 0
        
        return {
            'total_users': total_users,
            'average_preferences_per_user': avg_preferences,
            'most_common_preferences': self._get_most_common_preferences()
        }
    
    def _get_most_common_preferences(self) -> List[str]:
        """Get most common preference types."""
        preference_counts = {}
        for user_prefs in self.user_preferences.values():
            for pref_type in user_prefs.keys():
                preference_counts[pref_type] = preference_counts.get(pref_type, 0) + 1
        
        return sorted(preference_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _get_performance_trends(self) -> Dict:
        """Get performance trends."""
        return {
            'total_interactions': len(self.interaction_patterns),
            'average_success_rate': sum(p.success_rate for p in self.interaction_patterns.values()) / len(self.interaction_patterns) if self.interaction_patterns else 0,
            'learning_progress': 'active' if len(self.interaction_patterns) > 0 else 'initializing'
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on learned data."""
        recommendations = []
        
        if len(self.interaction_patterns) < 5:
            recommendations.append("Need more interaction data to generate meaningful insights")
        
        low_success_patterns = [p for p in self.interaction_patterns.values() if p.success_rate < 0.6]
        if low_success_patterns:
            recommendations.append(f"Found {len(low_success_patterns)} patterns with low success rates - consider improvements")
        
        return recommendations
    
    def _store_interaction_analysis(self, analysis: Dict):
        """Store interaction analysis for future learning."""
        # This would typically store to a database
        # For now, we'll just log it
        logger.info(f"Stored interaction analysis: {analysis}") 