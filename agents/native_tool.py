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