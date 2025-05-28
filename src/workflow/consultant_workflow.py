import os
from memory.vector_memory import VectorMemory
from workflow.agents import create_agents
from workflow.agent_selectors import human_in_the_loop_selector
from workflow.config import llm_config
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core.model_context import BufferedChatCompletionContext


async def main():
    async with VectorMemory(index_name=os.getenv("AZURE_SEARCH_INDEX_PROFILE")) as user_vector_memory:
        agent_config = llm_config("agent")
        tool_config = llm_config("tool")
        model_context = BufferedChatCompletionContext(buffer_size=10)

        # Create agents and user agent using modular function
        agents, user_agent = await create_agents(agent_config, tool_config)
        group_agents = agents + [user_agent]

        # Create SelectorGroupChat with imported selector
        groupchat = SelectorGroupChat(
            participants=group_agents,
            model_client=agent_config,
            max_turns=30,
            selector_func=human_in_the_loop_selector,
            model_context=model_context
        )

        print("Career Coach GroupChat: All agents can contribute in parallel.")
        user_message = input("Type your requirements as your first chat message: ")
        await groupchat.run(task=user_message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 