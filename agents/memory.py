from typing import Dict, List
from agents.base import BaseAgent
from models import ChatResponce
from ai_client import LLMService

class MemoryAgent(BaseAgent):
    def __init__(self):
        # define an inmemory dictionary to store conversation arrays mappped by session_id
        self.history: Dict[str, List[str]] ={}

        self.llm_serivce = LLMService()



    async def process_message(self, message:str, session_id:str) -> ChatResponce:
        #Check is the session is exist or not if not define new one, a empty history list for it 
        if session_id not in self.history:
            self.history[session_id] =[]

        # we append the user's incomming messagers to a single context payload for the AI 
        self.history[session_id].append({"role": "user", "content":message})

        # pass entire conversation timeline to groq 
        real_ai_reply = await self.llm_serivce.generate_response(self.history[session_id])

        # save the AI's real responce back into the history 
        self.history[session_id].append({"role":"assistant", "content":real_ai_reply})

        #We return theresponse along with the metadata showing the current length of the hirstory 
        return ChatResponce(
            model_used="memory",
            reply=real_ai_reply,
            metadata={"total_message": len(self.history[session_id])}
        )

        