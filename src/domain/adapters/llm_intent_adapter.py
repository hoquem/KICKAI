from domain.interfaces.llm_intent import LLMIntentExtractor
from utils.llm_intent import extract_intent as infrastructure_extract_intent


class LLMIntentExtractorAdapter(LLMIntentExtractor):
    """Adapter to convert infrastructure LLM intent extraction to domain interface."""
    
    def extract_intent(self, message: str, context=None) -> dict:
        return infrastructure_extract_intent(message, context=context) 