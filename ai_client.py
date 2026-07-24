import os
from dotenv import load_dotenv
from groq import AsyncGroq
from typing import List, Dict


# Load env variable 
load_dotenv()

class LLMService:
    def __init__(self):
        #ask api
        api_key = os.getenv("GROQ_API_KEY")

        #ensure api is initialize nefore client 
        if not api_key:
            raise ValueError("Groq_api_key is missing ")

        #Pass the loaded API key into AsyncGroq 
        self.client = AsyncGroq(api_key=api_key)

        # define default groq model identifier 
        self.model = "llama-3.1-8b-instant"

    # Add the optional tools patameter, 
    async def generate_response (self, message:List[Dict[str,str]], tools:List[Dict]=None):
        try:
            # Prepare a payload for groq
            kwargs={
                "messages":message,
                "model":self.model,
                "temperature":0.7,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] ="auto"

            #Send payload async to groq API
            completion = await self.client.chat.completions.create(**kwargs)
          
            
            msg = completion.choices[0].message

            # if the llm deside the call a tool, return the whole object 
            if msg.tool_calls: 
                return msg
            
            return msg.content

        except Exception as e:
            return f"[API Error]: Unable to generate responce -> {str(e)}"