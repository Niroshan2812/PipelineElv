import asyncio
import sys
from factory import AgentFactory

async def run_cli():

    # define a default session identifier doe the terminal user
    session_id = "cli_user"
    # initial starting mode to basic 
    current_mode = "basic"

    print("++++++++++++++++++++++++++++++ Moduler AI Agent CLI +++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print ("\n")
    print ("Commands: '/mode <name> (basic, memory, tools, mcp, skills, native_tool, react) | '/exit' to quit\n'")
    print ("\n")

    # run infinite loop 

    while True:
        try:
            user_input = await asyncio.to_thread(input, f"[{current_mode}] You: ")
        except (EOFError, KeyboardInterrupt):
            # We catch Ctrl+C or terminal EOF signals to exit cleanly without error tracebacks
            print("\nExiting CLI...")
            break

        # strip surrounding whitespace from the user string 
        clean_text = user_input.strip()

        #we ignore empty inputs when the user simply press Enter 
        if not clean_text:
            continue

        # check if the user enterd an exist command to terminate the script 
        if clean_text.lower() in ["/exit", "/quit", "exit", "quit"]:
            print("Goodbye!")
            break

        # slash commands to dynamically switch the active agent architecture 
        if clean_text.startswith("/mode"):
            # parse out the desired mode name fallowing the '/mode' perfix 
            new_mode = clean_text.split(" ",1)[1].strip().lower()

            #we validate the requested mode against our available factory classes 

            if new_mode in ["basic", "memory", "tools", "mcp", "skills", "native_tool", "react"]:
                current_mode = new_mode
                print(f"--> Switch activa agent to : [{current_mode.upper()}]\n")
            else:
                print(f"--> Unknown mode '{new_mode}'. Options: basic, memory, tools, mcp, skills, native_tool, react\n ")
            continue

        # we retrive the appropreate agent insrance from our factory based on the acvite mode 
        agent = AgentFactory.get_agent(current_mode)

        # Async execute agent's processinglogic using the user's input 
        response = await agent.process_message(clean_text, session_id)

        # print the AI'S text response directly to the termincal console 
        print(f"AI: {response.reply}")

        #We inspect and print any returned metadata 

        if response.metadata:
            print(f"    [Metadata]: {response.metadata}\n")
        else:
            print()


if __name__=="__main__":
    asyncio.run(run_cli())
