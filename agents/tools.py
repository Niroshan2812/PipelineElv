from agents.memory import MemoryAgent
from models import ChatResponce

class ToolAgent(MemoryAgent):
    """
    We inherit from Memory agent so we automatically get self,history and memory tracking 
    we add a specific tool execution layer on top of that memory 
    """

    def _execute_math_tool(self, expression:str) -> str:
        try:
            # we evaluate the mathemetic String to compute real answer 
            result = eval(expression)
            return str(result)

        except Exception as e:
            return f"Math error: {str(e)}"

    async def process_message(self, message:str, session_id:str) -> ChatResponce:
        # We CHECK if a memoty array exist or not 
        if session_id not in self.history:
            self.history[session_id] =[]

        self.history[session_id].append(f"User: {message}")

        # We check if the user prompt contains math symboles or trigger wordes like 'calculate'

        if "calculate " in message.lower() or any (op in message for op in ["+", "-", "*" ,"/"]):
            # We strip out the word calculate to isolate just the mathemetical equation 
            clan_expr = message.lower().replace("calculate", "").strip()

            # we execute our local python tool to solve the eqyation 
            tool_output  = self._execute_math_tool(clan_expr)

            # format the AI reply to show that specific tool was invokes and display result 
            reply = f"[Tool Mode] I invoked the Math Calculator Tool. The result of ({clan_expr}) is {tool_output}"


        else:
            # We fall back to a standard conversational response if no math tool trigger is detected
            reply = f"[Tool Mode] No math tools required for this prompt. You said: '{message}'"

        self.history[session_id].append(f"AI:{reply}")

        return ChatResponce(
            model_used="tools",
            reply=reply,
            metadata={
                "tool_turns": len(self.history[session_id]),
                "tool_used": "Math Calculator" if "calculate" in message.lower() or any (op in message for op in ["+", "-","*","/"]) else "None"
            }
        )