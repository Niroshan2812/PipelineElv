import httpx
from typing import Dict, List, Any
from agents.memory import MemoryAgent
# Note: Ensure the spelling below matches your actual models.py file (ChatResponse vs ChatResponce)
from models import ChatResponce 
from ai_client import LLMService

class MCPAgent(MemoryAgent):
    """
    We inherit from MemoryAgent to retain conversational history.
    We add networking capability to communicate with external MCP servers for tool execution.
    """
    def __init__(self):
        # We initialize the parent memory structure
        super().__init__()
        
        # We define a dictionary to retain structured message arrays for conversational memory
        self.history: Dict[str, List[Dict[str, str]]] = {}

        # We initialize the live Groq API service (Fixed typo: llm_serivce -> llm_service)
        self.llm_service = LLMService()

        # We map specialized server endpoints to distinct local ports
        self.math_server_url = "http://127.0.0.1:8081/mcp"
        self.file_server_url = "http://127.0.0.1:8082/mcp"

    async def _call_remote_server(self, url: str, payload: Dict[str, Any]) -> str:
        # We send an asynchronous POST request to the target MCP endpoint
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=3.0)
                # We return the extracted result string or a default fallback message
                return response.json().get("result", "No result returned.")
            except Exception as e:
                # We catch connection errors if the target microservice is offline
                return f"[Connection Error]: Could not reach server at {url}. Details: {str(e)}"

    async def process_message(self, message: str, session_id: str) -> ChatResponce:
        # We initialize memory for the session if it does not already exist
        if session_id not in self.history:
            self.history[session_id] = []

        # We append the incoming user message to the conversation timeline
        self.history[session_id].append({"role": "user", "content": message})

        msg_lower = message.lower()
        tool_data = None
        server_used = "None"

        # We route file operations to Port 8082 based on intent keywords
        if any(kw in msg_lower for kw in ["file", "create", "write", "read", "delete"]):
            # We parse deletion intent from the natural language string
            is_delete = "delete" in msg_lower
            
            # We check if the user included confirmation keywords in their prompt
            confirm = any(kw in msg_lower for kw in ["confirm", "yes", "confirm_delete:true", "confirm_delete", "true"])

            # We construct the file payload, ensuring the parameter name is strictly confirm_delete
            payload = {
                "action": "delete" if is_delete else ("write" if "write" in msg_lower else "create"),
                "filename": "demo.txt",
                "content": message,
                "confirm_delete": confirm
            }
            # We execute the remote call to the file server
            tool_data = await self._call_remote_server(self.file_server_url, payload)
            server_used = f"FileSystem MCP ({self.file_server_url})"

        # We route advanced math calculations to Port 8081
        elif any(kw in msg_lower for kw in ["calculate", "sin", "cos", "sqrt", "log", "*", "/", "+"]):
            # We clean the text to isolate just the mathematical equation
            clean_expr = message.replace("calculate", "").strip()
            tool_data = await self._call_remote_server(self.math_server_url, {"query": clean_expr})
            server_used = f"Math MCP ({self.math_server_url})"

        # We inject retrieved MCP tool data into the conversational context for Groq to process
        if tool_data:
            # We apply strict guardrails to prevent Groq from hallucinating success on API rejection
            system_injection = (
                f"SYSTEM NOTICE: The backend API tool executed and returned this exact result: '{tool_data}'. "
                "CRITICAL RULE: If the result contains words like 'Rejected', 'Error', or 'Denied', "
                "you MUST inform the user that the operation FAILED and state the exact reason. "
                "Do NOT claim the file was deleted or created unless the API result explicitly confirms success."
            )
            # We append the system instruction directly into the session history
            self.history[session_id].append({"role": "system", "content": system_injection})

        # We call the real Groq LLM with our updated memory and tool context
        groq_reply = await self.llm_service.generate_response(self.history[session_id])

        # We store Groq's final generated answer in session memory
        self.history[session_id].append({"role": "assistant", "content": groq_reply})

        # We return the standardized response back to the CLI or router
        return ChatResponce(
            model_used="mcp",
            reply=groq_reply,
            metadata={
                "total_turns": len(self.history[session_id]),
                "server_used": server_used,
                "tool_raw_output": tool_data
            }
        )