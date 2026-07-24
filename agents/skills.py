
from agents.memory import MemoryAgent
from typing import Dict
from models import ChatResponce


class SkillAgent (MemoryAgent):
    """
    We inherit from MemoryAgent to maintain conversational context.
    We add a 'Skills Registry' to dynamically inject domain-specific instructions (system prompts).
    """

    def __init__(self):
        super().__init__()

        # We define a registry of specialized system prompts that act as distinct AI skills
        self.skills_registry: Dict[str, str] = {
            "coding": "Skill [Software Engineer]: Focus on clean OOP architecture, design patterns, and performance.",
            "data": "Skill [Data Analyst]: Focus on statistical accuracy, data visualization, and SQL optimization.",
            "default": "Skill [General Assistant]: Provide clear, direct, and helpful answers."
        }

    def _select_skill(self, message:str)->str:
        # we imspec the user message keywords to dynamiclly slelect the appropreate domain skill 
        msg_lower = message.lower()

        if any(kw in msg_lower for kw in ["code", "java", "python", "bug", "oop", "class"]):
            return self.skills_registry["coding"]
        elif any(kw in msg_lower for kw in ["data", "sql", "chart", "average", "database"]):
            return self.skills_registry["data"]

        return self.skills_registry["default"]

    async def process_message(self, message: str, session_id:str) -> ChatResponce:

        # session histroy array if not exist 
        if session_id not in self.history:
            self.history[session_id] =[]

        # resolve which spesific skill rpofile shoulf be activate dfor this prompt 
        active_skill = self._select_skill(message)

        #append the incoming user message to conversation timeline 
        self.history[session_id].append(f"User: {message}")

        #we simulate the LLM generation 
        reply = f"[Skills Mode] Activating {active_skill} -> Processed: '{message}'"
        
        # We save the AI reply back into the session history
        self.history[session_id].append(f"AI: {reply}")


        return ChatResponce(
            model_used="skilled ",
            reply = reply,
            metadata={
                "total_turns": len(self.history[session_id]),
                "active_skill": active_skill
            }
        )
      