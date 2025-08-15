"""
LLM Intent Extraction Utility

This module provides LLM-based intent extraction functionality for natural language processing
in the KICKAI system using CrewAI agents and structured output.
"""

import json
from typing import Any, Dict, Union, Optional
from dataclasses import dataclass

from loguru import logger
from crewai import Agent, Task, Crew
from kickai.config.llm_config import get_llm_config
from kickai.core.enums import AgentRole


@dataclass
class IntentResult:
    """Structured result for intent recognition."""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    reasoning: str
    original_message: str


class LLMIntentRecognizer:
    """
    Pure LLM-based intent recognition using CrewAI agents.
    
    This replaces the regex-based approach with sophisticated LLM understanding
    that can handle context, paraphrases, and complex natural language.
    """

    def __init__(self, team_id: str = None):
        self.team_id = team_id
        self.llm_config = get_llm_config()
        self.llm = self.llm_config.get_main_llm()
        self.agent = self._create_intent_agent()
        logger.info(f"🤖 LLMIntentRecognizer initialized for team: {team_id}")

    def _create_intent_agent(self) -> Agent:
        """Create the intent recognition agent."""
        return Agent(
            role="Intent Recognition Specialist",
            goal="Accurately identify user intent and extract relevant entities from natural language messages in a football team management context",
            backstory="""You are an expert at understanding user intent in football team management contexts.
            
            You specialize in:
            - Understanding football terminology and team management concepts
            - Recognizing user communication patterns and paraphrases
            - Extracting relevant entities and context from messages
            - Providing confidence scores based on your analysis
            - Explaining your reasoning for intent classification
            
            You understand that users may express the same intent in many different ways,
            and you can handle context, ambiguity, and conversational language effectively.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False
        )

    async def extract_intent(self, message: str, context: Dict[str, Any] = None) -> IntentResult:
        """
        Extract intent using LLM-based analysis.
        
        Args:
            message: The input message to analyze
            context: Additional context (chat_type, user_role, etc.)
            
        Returns:
            IntentResult with intent, confidence, entities, and reasoning
        """
        try:
            # Create the intent analysis task
            task = self._create_intent_task(message, context or {})
            
            # Create a simple crew with just the intent agent
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=False,
                process="sequential"
            )
            
            # Execute the task
            result = await crew.kickoff()
            
            # Parse the structured result
            return self._parse_llm_result(result, message)
            
        except Exception as e:
            logger.error(f"❌ Error in LLM intent extraction: {e}")
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                entities={},
                reasoning=f"Error during intent extraction: {str(e)}",
                original_message=message
            )

    def _create_intent_task(self, message: str, context: Dict[str, Any]) -> Task:
        """Create the intent analysis task."""
        
        context_info = self._format_context(context)
        
        task_description = f"""
        Analyze this user message and determine their intent in the context of a football team management system.

        USER MESSAGE: "{message}"
        
        CONTEXT: {context_info}
        
        AVAILABLE INTENTS:
        1. get_player_info - User wants information about themselves or another player
           Examples: "What's my phone number?", "Show me my details", "Am I registered?", "What's my position?"
           
        2. update_profile - User wants to update their information
           Examples: "I need to change my phone number", "Update my position", "Modify my details"
           
        3. get_team_info - User wants information about the team or players
           Examples: "Show me all players", "List the team", "Who's on the team?"
           
        4. get_help - User needs help or assistance
           Examples: "Help me", "What can you do?", "How do I use this?", "I need assistance"
           
        5. filter_players - User wants to filter or search players
           Examples: "Show me goalkeepers", "Who's available?", "Players in midfield"
           
        6. get_team_stats - User wants team statistics
           Examples: "How many players do we have?", "Team statistics", "Player count"
           
        7. unknown - Cannot determine intent or doesn't fit other categories

        REQUIREMENTS:
        1. Analyze the message carefully considering context and football terminology
        2. Identify the most likely intent from the available options
        3. Extract relevant entities (player names, positions, info types, etc.)
        4. Provide a confidence score (0.0-1.0) based on how certain you are
        5. Explain your reasoning for the classification
        6. Return your analysis in this exact JSON format:
        {{
            "intent": "intent_name",
            "confidence": 0.85,
            "entities": {{
                "player_name": "John Doe",
                "info_type": "phone",
                "position": "midfielder"
            }},
            "reasoning": "The user is asking about their personal information, specifically their phone number, which falls under get_player_info intent."
        }}

        IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON object with intent, confidence, entities, and reasoning"
        )

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the task."""
        if not context:
            return "No additional context provided"
        
        context_parts = []
        for key, value in context.items():
            if value is not None:
                context_parts.append(f"{key}: {value}")
        
        return ", ".join(context_parts) if context_parts else "No additional context provided"

    def _parse_llm_result(self, result: str, original_message: str) -> IntentResult:
        """Parse the LLM result into a structured IntentResult."""
        try:
            # Clean the result - remove any markdown formatting
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
            cleaned_result = cleaned_result.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned_result)
            
            return IntentResult(
                intent=parsed.get("intent", "unknown"),
                confidence=float(parsed.get("confidence", 0.0)),
                entities=parsed.get("entities", {}),
                reasoning=parsed.get("reasoning", "No reasoning provided"),
                original_message=original_message
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"❌ Error parsing LLM result: {e}")
            logger.error(f"Raw result: {result}")
            
            # Fallback parsing - try to extract intent from text
            return self._fallback_parse(result, original_message)

    def _fallback_parse(self, result: str, original_message: str) -> IntentResult:
        """Fallback parsing when JSON parsing fails."""
        try:
            # Try to extract intent from the text response
            result_lower = result.lower()
            
            intent_mapping = {
                "get_player_info": ["player", "info", "details", "phone", "position", "registration"],
                "update_profile": ["update", "change", "modify", "edit"],
                "get_team_info": ["team", "players", "list", "show"],
                "get_help": ["help", "assist", "support"],
                "filter_players": ["filter", "search", "goalkeeper", "defender", "midfielder"],
                "get_team_stats": ["stats", "statistics", "count", "how many"]
            }
            
            detected_intent = "unknown"
            confidence = 0.3  # Low confidence for fallback
            
            for intent, keywords in intent_mapping.items():
                if any(keyword in result_lower for keyword in keywords):
                    detected_intent = intent
                    confidence = 0.5
                    break
            
            return IntentResult(
                intent=detected_intent,
                confidence=confidence,
                entities={},
                reasoning=f"Fallback parsing used due to JSON parsing error. Raw response: {result[:200]}...",
                original_message=original_message
            )
            
        except Exception as e:
            logger.error(f"❌ Error in fallback parsing: {e}")
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                entities={},
                reasoning=f"Complete parsing failure: {str(e)}",
                original_message=original_message
            )


# Clean async-only implementation - no backward compatibility
# Use LLMIntentRecognizer class directly for all intent recognition needs


class LLMIntent:
    """Legacy class for backward compatibility."""
    
    def __init__(self, team_id: str = None):
        self.team_id = team_id
        self.recognizer = LLMIntentRecognizer(team_id)
        logger.info(f"🤖 LLMIntent initialized for team: {team_id}")

    async def extract_intent(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Extract intent using LLM-based approach.
        """
        context_dict = {"context": context} if context else {}
        result = await self.recognizer.extract_intent(message, context_dict)
        
        return {
            "intent": result.intent,
            "entities": result.entities,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
