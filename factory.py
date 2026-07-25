from agents.base import BaseAgent
from agents.basic import BasicAgent
from agents.memory import MemoryAgent
from agents.tools import ToolAgent
from agents.mcp import MCPAgent
from agents.skills import SkillAgent
from agents.native_tool import NativeToolAgent
from agents.react import ReActAgent

class AgentFactory: 
    # We register our available agent instancess in a static directory for o(1) lookup 

    _agents ={
        "basic" :BasicAgent(),
        "memory": MemoryAgent(),
        "tools": ToolAgent(),
        "mcp": MCPAgent(),
        "skills":SkillAgent(),
        "native_tool":NativeToolAgent(),
        "react": ReActAgent()
    }
    @classmethod
    def get_agent(cls, mode:str) ->BaseAgent:
        # We retrive the requested agent by it's name, Defalting safely to basic agent 
        return cls._agents.get(mode.lower(),cls._agents["basic"])