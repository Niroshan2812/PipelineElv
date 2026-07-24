from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    # We define an explicit mode to allow switching between diffrant agent architecture 
    model:str
    message:str
    session_id :Optional[str]="default-user"

class ChatResponce(BaseModel):
    model_used: str
    reply:str
    metadata:Optional[Dict[str, Any]] = None

