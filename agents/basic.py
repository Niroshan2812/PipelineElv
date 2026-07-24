from agents.base import BaseAgent
from models import ChatResponce
from ai_client import LLMService

class BasicAgent(BaseAgent):
    """"
        We handle a direct, steteless LLM instruction here 
        No history, No tools 
    """
    def __init__(self):
        self.llm_service = LLMService()

    async def process_message(self, message:str, session_id:str) -> ChatResponce:

        message_payload = [{"role":"user", "content":message}]

        real_ai_reply = await self.llm_service.generate_response(message_payload)

        return ChatResponce(model_used="baisc", reply=real_ai_reply)
