# We imopt fst api to run our standeron math service and pynantic for data validation 

from fastapi import FastAPI
from pydantic import BaseModel
import math
import cmath

app= FastAPI(title="Mathemetics MCP server ")

# json schema form incomming client request 

class MathRequest(BaseModel):
    query:str

@app.post("/mcp")
async def execute_math_tool(payload:MathRequest):
    # Extract the mathemetical body from the client req
    print(MathRequest)
    expression = payload.query.strip()
    print(expression)


    try:
        # safe fictionay of allowed mathemetical functions 
        safe_functions={
            "sin":math.sin, "cos":math.cos, "tan":math.tan,  
             "sqrt":math.sqrt, "log":math.log, "log10":math.log10, 
              "pi":math.pi, "e":math.e, "pow":math.pow, "csqrt":cmath.sqrt
        }

        # evaluate the mathemetical String using only our approved function dictionary

        result = eval(expression, {"__builtins__":None}, safe_functions)

        # return the computed number inside our standerd JSON result wrapper
        return {"result":f"Math Server output: {expression} = {result}"}
    except Exception as e:
        # invaid syntax or divison by zero and return an error message 
        return {"result": f"Math server Error:  Cannot evaluate '{expression}'. Reason: {str(e)}"}