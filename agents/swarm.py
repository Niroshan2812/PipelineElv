from agents import tools
import json
from agents.memory import MemoryAgent
from models import ChatResponce

# import specilized sub agents 
from agents.react import ReActAgent
from agents.skills import SkillAgent
from agents.rag import RAGAgent

class SwarmAgent(MemoryAgent):
    """
    Acts as a 'Manager Agent'. It doesn't solve the problem directly.
    Instead, it analyzes the prompt and delegates the work to specialized sub-agents.
    """

    def __init__(self):
        super().__init__()

        self.routing_schema =[
             {
                "type": "function",
                "function": {
                    "name": "delegate_task",
                    "description": "Delegates the user's prompt to a specialized sub-agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_type": {
                                "type": "string",
                                "enum": ["react", "skills", "rag"],
                                "description": "Use 'rag' if the user asks about past conversations, previous details, or things they told you earlier. Use 'react' for math/files..."
                            },
                            "instructions": {
                                "type": "string",
                                "description": "The specific instruction to give to the sub-agent."
                            }
                        },
                        "required": ["agent_type", "instructions"]
                    }
                }
            }
        ]
    

    async def process_message(self, message:str, session_id:str) -> ChatResponce:
        # we telll the LLM it is a manager and must delegate 

        message = [
            {"role": "system", "content": "You are a Swarm Manager. You MUST NOT answer the user's prompt yourself. You MUST use the delegate_task tool to route EVERY request to the correct sub-agent."},
            {"role": "user", "content": message}
        ]

        # call groq with our routing menu
        ai_responce = await self.llm_serivce.generate_response(message, tools=self.routing_schema)

        if not isinstance(ai_responce, str) and hasattr(ai_responce, "tool_calls") and ai_responce.tool_calls:
            tool_call =ai_responce.tool_calls[0]
            args = json.loads(tool_call.function.arguments)

            target_agent = args["agent_type"]
            instructions = args["instructions"]

            print(f"[SWARM MANAGER] rouring request to -> {target_agent.upper()} agent")
            print(f"[SWARM MANAGER]instruction passed -> {instructions}\n" )


            # Instructing sub agents dynamically 

            if target_agent == "react":
                sub_agent = ReActAgent()
            elif target_agent == "skills":
                sub_agent = SkillAgent()
            else:
                sub_agent = RAGAgent()

            # sub agents process the messafe and get its responce 
            sub_session = f"{session_id}_{target_agent}"
            sub_response = await sub_agent.process_message(instructions, sub_session)

            return ChatResponce(
                model_used=f"swarm_delegated_to_{target_agent}",
                reply=sub_response.reply,
                metadata={"manager_decision": f"Delegated to {target_agent}"}
            )
        else:
            return ChatResponce(
                model_used="swarm_manager",
                reply="I couldn't decide who to delegate this to. Please be more specific."
            )

            

        