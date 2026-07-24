from fastapi import FastAPI
from models import ChatResponce, ChatRequest
from agents.basic import BasicAgent
from factory import AgentFactory

app = FastAPI(title="Evolunary Agent Architecture ")

# Witnput memory

# basic_agent = BasicAgent()

# @app.post("/chat", response_model=ChatResponce)

# async def chat_endpoint(requirest:ChatRequiremnt):
#     response = await basic_agent.process_message(requirest.message, requirest.session_id)

#     return response

## ___________________________________________________________________________________
## - This is second one we calling the using memory 

@app.post("/chat", response_model=ChatResponce)
async def chat_endpoint(request:ChatRequest):
    # We use the factory to dynamically resolve the correct agent implementation based on the requested mode
    agent = AgentFactory.get_agent(request.model)

    # We execute the message processing polymorphyically without needing to know the agent's internal log 
    responce = await agent.process_message(request.message, request.session_id)
    #We return the sanderlized JSON playback to client 
    return responce

