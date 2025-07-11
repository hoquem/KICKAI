from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMIntentExtractor(ABC):
    """Domain interface for LLM intent extraction."""
    
    @abstractmethod
    def extract_intent(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract intent and entities from a message.
        
        Args:
            message: The user's message
            context: Optional context information
            
        Returns:
            Dictionary containing intent, confidence, and entities
        """
        pass 