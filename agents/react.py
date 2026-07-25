import json
from agents.native_tool import NativeToolAgent
from models import ChatResponce

class ReActAgent(NativeToolAgent):

    """
    Inherits from NativeToolAgent to reuse the tool schema and remote server calls.
    Overrides process_message to introduce a 'While' loop for autonomous execution.
    """

    async def process_message(self, message:str,session_id:str) -> ChatResponce:

        #initialized history
        if session_id not in self.history:
            self.history[session_id] =[]

        
        #append new user prompt 
        self.history[session_id].append({"role":"user","content":message})

        # track how many ai has run - for prevent infinite loop 

        iteration_count =0
        max_iteration =5
        server_used=[]

        # ReAct loop 
        while iteration_count < max_iteration:
            print(f"/n [react_loop] Thinking.... (iteration {iteration_count +1})")

            # ask ai to what do next 
            ai_responce = await self.llm_serivce.generate_response(
                self.history[session_id],
                tools=self.tool_schema
            )
            #if the ai did not call a tool, it may have finished it goal
            if isinstance(ai_responce,str) or not hasattr(ai_responce, "tool_calls") or not ai_responce.tool_calls:
                
                final_reply = ai_responce.content if hasattr(ai_responce,"content")else str(ai_responce)
                self.history[session_id].append({"role":"assistant", "content":final_reply})

                return ChatResponce(
                    model_used="react_loop",
                    reply=final_reply,
                    metadata={
                        "iterations" : iteration_count +1,
                        "servers_used": ",".join(server_used) if server_used else "None"
                    }
                )
                # if te ai did call a tool, we execute it 
            tool_call = ai_responce.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f" -> AI disided to act: calling '{function_name}' with args {arguments}")

            tool_data = "error: tool not found "

            if function_name == "math_calculator":
                tool_data = await self._call_remote_server(
                    self.math_server_url,
                    {"query": arguments["expression"]}
                )
                if "Math MCP" not in server_used:
                    server_used.append("Math MCP")

            print (f"-> Observed result: {tool_data}")
                
            # Append observation backto history so ai can reason about it 
            # 
            # 
            self.history[session_id].append(ai_responce)

            # append actial tool output 
            self.history[session_id].append({
                "role":"tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": str(tool_data)
            }) 
            iteration_count += 1

        # if we hit max iteration, we farce the loop to stop 
        fallback_reply = "I reached maximum thinking steps and had to stop"
        self.history[session_id].append({"role": "assistant", "content": fallback_reply})

        return ChatResponce(
            model_used="react_loop",
            reply=fallback_reply,
            metadata={"iterations": iteration_count}
        )

                    
               