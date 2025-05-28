from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.tools import AgentTool

def make_analyze_resume_tool(tool_client):
    """Analyze a resume for strengths, weaknesses, and ATS optimization."""
    analyze_resume_agent = AssistantAgent(
        name="AnalyzeResumeAgent",
        description="Analyze a resume for strengths, weaknesses, and ATS optimization. You need to give actionable feedback.",
        model_client=tool_client,
        system_message="You are a resume analyzer. You are given a resume and you need to analyze it for strengths, weaknesses, and ATS optimization. You need to give actionable feedback.",
    )
    return AgentTool(analyze_resume_agent)

def make_analyze_skill_gap_tool(tool_client):
    """Compare user skills to job requirements and identify gaps."""
    analyze_skill_gap_agent = AssistantAgent(
        name="AnalyzeSkillGapAgent",
        description="Compare user skills to job requirements and identify gaps.",
        model_client=tool_client,
        system_message="You are a skill gap analyzer. You are given user skills and job requirements and you need to identify gaps.",
    )
    return AgentTool(analyze_skill_gap_agent)
