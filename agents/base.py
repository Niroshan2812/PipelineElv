from abc import ABC, abstractmethod
from models import ChatResponce

class BaseAgent(ABC):
    """
    We use an abstract base class to enfoce a stric content 
    Every feature agent must implment this exact method
    """

    @abstractmethod
    async def process_message(self, message:str, session_id:str) -> ChatResponce:
        pass
