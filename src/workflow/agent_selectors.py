def human_in_the_loop_selector(messages):
    """
    Selector for AutoGen SelectorGroupChat.
    - messages: list of BaseAgentEvent or BaseChatMessage objects
    Returns the name (string) of the next speaker.
    """
    # Define all non-user agent names
    all_non_user_agents = ["TriageAgent", "ProfilerAgent", "SkillAgent", "LearningPlanAgent", "GlobalJobsAgent"]
    agent_names = []
    last_speaker = None
    for msg in messages:
        name = getattr(msg, "source", None)
        if name == "user":
            name = "user_proxy"
        if name and name not in agent_names:
            agent_names.append(name)
        last_speaker = name or last_speaker

    # Debug prints
    if last_speaker and last_speaker != 'user_proxy':
        print(f"[{last_speaker}]: {messages[-1].to_text()}")
    # print("--------------------------------")

    # Always include user_proxy
    if "user_proxy" not in agent_names:
        agent_names.append("user_proxy")

    # If this is the very first message (or only user_proxy has spoken), start with TriageAgent
    if not messages or (len(agent_names) == 1 and agent_names[0] == "user_proxy"):
        return "TriageAgent"

    # If last message is a question or requests user input, return user_proxy
    if messages:
        last_msg = messages[-1].to_text()
        if (
            last_msg.strip().endswith("?")
            or "please provide" in last_msg.lower()
            or "can you" in last_msg.lower()
            or "user input" in last_msg.lower()
        ):
            return "user_proxy"

    # Round-robin among all non-user agents
    non_user_agents = all_non_user_agents
    if last_speaker and last_speaker in non_user_agents:
        idx = non_user_agents.index(last_speaker)
        next_idx = (idx + 1) % len(non_user_agents)
        selected = non_user_agents[next_idx]
        return selected
    # Start with TriageAgent or first non-user agent
    if "TriageAgent" in non_user_agents:
        selected = "TriageAgent"
    else:
        selected = non_user_agents[0] if non_user_agents else "user_proxy"
    return selected 