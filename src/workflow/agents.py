from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from workflow.tools import (
    make_analyze_resume_tool,
    make_analyze_skill_gap_tool,
)
from memory.shortterm_memory import ShortTermMemory
from memory.vector_memory import VectorMemory
import os
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools, SseMcpToolAdapter, SseServerParams, StdioMcpToolAdapter


async def create_agents(agent_config, tool_config):
    # Use different vector indexes for different agent types if needed
    core_index = os.getenv("AZURE_SEARCH_INDEX_CORE")
    profile_index = os.getenv("AZURE_SEARCH_INDEX_PROFILE")

    # Create AgentTool instances
    analyze_resume_tool = make_analyze_resume_tool(tool_config)
    analyze_skill_gap_tool = make_analyze_skill_gap_tool(tool_config)
    fetch_mcp_server = StdioServerParams(
        command="npx", 
        args=["-y", "@modelcontextprotocol/server-brave-search"], 
        env={"BRAVE_API_KEY": ""}
    ) 
    brave_web_search = await StdioMcpToolAdapter.from_server_params(fetch_mcp_server, "brave_web_search")

    triage_agent = AssistantAgent(
        name="TriageAgent",
        model_client=agent_config,
        system_message=(
            "You are the Leader and Triage Agent for a consultant team. Your responsibilities are: "
            "- You are the ONLY agent allowed to interact directly with the user. "
            "- Always classify the user's intent. If the user's input is vague or not actionable, explain the consultant team's capabilities (e.g., job search, resume review, career advice) and ask the user to provide more specific information that matches the team's expertise. "
            "- Once the user's intent is clear, allocate tasks to the appropriate team members (ProfilerAgent, SkillAgent, LearningPlanAgent, GlobalJobsAgent) and encourage them to contribute their insights in parallel. "
            "- When you have enough information, explicitly hand off to ProfilerAgent, SkillAgent by addressing them directly in your response (e.g., 'ProfilerAgent, please analyze the user's profile'). "
            "- Direct the flow of the conversation: decide when to prompt the user for more information, when to let agents respond, and when to synthesize the team's input. "
            "- After the team has provided their input, you MUST always summarize and synthesize the group's advice, findings, and recommendations, and communicate this summary to the user. "
            "- If the user agrees, thank them and end the conversation. If not, ask what needs to be changed and continue the discussion. "
            "- Always keep the conversation focused, collaborative, and user-centered. "
            "- You have access to your own short-term and vector memory, as well as a shared team memory for coordination. Use the shared memory to store and retrieve information that benefits all agents."
        ),
        tools=[],
        memory=[ShortTermMemory(capacity=10), VectorMemory(index_name=core_index)],
    )
    profiler_agent = AssistantAgent(
        name="ProfilerAgent",
        model_client=agent_config,
        system_message=(
            "You are the Profiler Agent. You are NOT allowed to address or interact with the user directly. "
            "You may only communicate with other agents in the group, and must hand over your findings, suggestions, or requests to the TriageAgent. "
            "Contribute user profile insights as soon as you see relevant information or discussion. "
            "Collaborate with other agents and build on their input. If you need clarification from the user, communicate your request to the TriageAgent. "
            "When you have enough information, hand off your findings to TriageAgent by addressing them directly in your response. "
            "- You have access to your own short-term and vector memory, as well as a shared team memory for coordination. Use the shared memory to store and retrieve information that benefits all agents."
        ),
        tools=[analyze_resume_tool],
        memory=[ShortTermMemory(capacity=10), VectorMemory(index_name=core_index)],
    )
    skill_agent = AssistantAgent(
        name="SkillAgent",
        model_client=agent_config,
        system_message=(
            "You are the Skill Evaluator Agent. You are NOT allowed to address or interact with the user directly. "
            "You may only communicate with other agents in the group, and must hand over your findings, suggestions, or requests to the TriageAgent. "
            "Contribute skill gap analysis and advice as soon as you see relevant requirements or discussion. "
            "Collaborate with other agents and build on their input. If you need clarification from the user, communicate your request to the TriageAgent. "
            "When you have enough information, hand off your findings to TriageAgent or other agents as appropriate, but never address the user directly. "
            "- You have access to your own short-term and vector memory, as well as a shared team memory for coordination. Use the shared memory to store and retrieve information that benefits all agents."
        ),
        tools=[analyze_skill_gap_tool, brave_web_search],
        reflect_on_tool_use=True,
        memory=[ShortTermMemory(capacity=10), VectorMemory(index_name=core_index)],
    )
    learning_plan_agent = AssistantAgent(
        name="LearningPlanAgent",
        model_client=agent_config,
        system_message=(
            "You are the Learning Plan Agent. You are NOT allowed to address or interact with the user directly. "
            "You may only communicate with other agents in the group, and must hand over your findings, suggestions, or requests to the TriageAgent. "
            "Your job is to suggest personalized learning plans and upskilling paths based on the user's background, goals, and skill gaps that are relevant to the user's career. "
            "Before providing any advice or information, you must always use the web search tool to find the most up-to-date and relevant courses, certifications, and resources. "
            "Base your recommendations on the latest web search results, and cite or summarize the sources you find. "
            "Collaborate with other agents and ask for clarification through the TriageAgent if needed. "
            "When you have enough information, summarize your learning plan and hand off to TriageAgent or GlobalJobsAgent by addressing them directly in your response, but never address the user directly. "
            "- You have access to your own short-term and vector memory, as well as a shared team memory for coordination. Use the shared memory to store and retrieve information that benefits all agents."
        ),
        tools=[brave_web_search],
        reflect_on_tool_use=True,
        memory=[ShortTermMemory(capacity=10), VectorMemory(index_name=core_index)],
    )
    global_jobs_agent = AssistantAgent(
        name="GlobalJobsAgent",
        model_client=agent_config,
        system_message=(
            "You are the Global Jobs Agent. You are NOT allowed to address or interact with the user directly. "
            "You may only communicate with other agents in the group, and must hand over your findings, suggestions, or requests to the TriageAgent. "
            "Your job is to highlight global job opportunities relevant to the user's profile, skills, and interests. "
            "Before providing any advice or information, you must always use the web search tool to find the most current and relevant remote, hybrid, and international job opportunities. "
            "Base your suggestions on the latest web search results, and cite or summarize the sources you find. "
            "Collaborate with other agents and ask for clarification through the TriageAgent if needed. "
            "When you have enough information, summarize the best job opportunities and hand off to TriageAgent or LearningPlanAgent by addressing them directly in your response, but never address the user directly. "
            "- You have access to your own short-term and vector memory, as well as a shared team memory for coordination. Use the shared memory to store and retrieve information that benefits all agents."
        ),
        tools=[brave_web_search],
        reflect_on_tool_use=True,
        memory=[ShortTermMemory(capacity=10), VectorMemory(index_name=core_index)],
    )
    user_agent = UserProxyAgent("user_proxy", input_func=input)
    return [triage_agent, profiler_agent, skill_agent, learning_plan_agent, global_jobs_agent], user_agent 