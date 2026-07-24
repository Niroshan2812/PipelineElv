import json
# pyrefly: ignore [missing-import]
from agents.mcp import MCPAgent
from models import ChatResponce

class NativeToolAgent(MCPAgent):

    """
    Inherits from MCPAgent to keep the memory and server connection logic.
    But overrides process_message to use Native Function Calling instead of keywords.
    """

    def __init__(self):
        super().__init__()

        # this is an menu We teaching the LLM what tools it can use 
        self.tool_schema = [
            {
                "type": "function",
                "function": {
                    "name": "math_calculator",
                    "description": "Evaluates a mathematical expression and returns the result.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The math expression to evaluate (e.g., '2+2', 'sqrt(16)')"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]
    
    async def process_message(self,message:str, session_id:str) -> ChatResponce:

        # initialize history
        if session_id not in self.history:
            self.history[session_id]=[]

        # add use message
        self.history[session_id].append({"role": "user", "content": message})

        #call the LLM, parsing menu of tools
        ai_response = await self.llm_service.generate_response(
            self.history[session_id],
            tools=self.tool_schema
        )

        tool_data = None
        server_used ="None"

        # check if the ai decided to call a tool instead of reply with text 

        if ai_response.tool_calls:
            #get te first tool AI wants to use 
            tool_call = ai_response.tool_calls[0]

            #The ai tell extract name of the function 
            function_name = tool_call.function.name

            # the ai give a json string of srg 
            # pass the json string into a pyhton dic
            arguments = json.loads(tool_call.function.arguments)

            print(f"\n[DEBUG] LLM Requested Tool: {function_name}")
            print(f"[DEBUG] LLM Generated Args: {arguments}\n")

            # route the tool call to remote mcp servers 

            if function_name == "math_calculator":
                tool_data = await self._call_remote_server(
                    self.math_server_url,
                    {"query":arguments["expression"]}
                ) 
                server_used =f"Math MCP ({self.math_server_url})"
            
            #inject the tools result back into the conversation history
            self.history[session_id].append({
                "role":"tool",
                "name":function_name,
                "content":str(tool_data)
            })

            # call the LLM one more time so it can read tool result and answer the user 
            ai_response = await self.llm_serivce.generate_response(self.history[session_id])

        final_reply = ai_response.content if hasattr(ai_response,"content") else str(ai_response)
        
        self.history[session_id].append({"role":"assistant","content":final_reply})

        return ChatResponce(
            model_used="native_tool",
            reply = final_reply,
            metadata={
                "server_used": server_used,
                "tool_raw_output": tool_data
            }
        )