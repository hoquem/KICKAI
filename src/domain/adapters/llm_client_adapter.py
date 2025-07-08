from domain.interfaces.llm_client import LLMClient
from utils.llm_client import LLMClient as InfrastructureLLMClient


class LLMClientAdapter(LLMClient):
    """Adapter to convert infrastructure LLM client to domain interface."""
    
    def __init__(self):
        self._client = InfrastructureLLMClient()
    
    async def generate_response(self, prompt: str, context=None) -> str:
        return await self._client.generate_response(prompt, context=context)
    
    async def analyze_text(self, text: str, analysis_type: str) -> dict:
        return await self._client.analyze_text(text, analysis_type) 