"""
adapters/crewai/crew.py — CrewAI Crew assembly
"""


def build_research_crew():
    try:
        from crewai import Agent, Task, Crew, Process
    except ImportError:
        raise ImportError("pip install crewai")

    from adapters.crewai.tools import get_crewai_tools
    from domain.prompts.researcher import RESEARCHER_SYSTEM_PROMPT
    from domain.prompts.analyst import ANALYST_SYSTEM_PROMPT, REPORTER_SYSTEM_PROMPT

    tools       = get_crewai_tools()
    search_tool = tools[0]
    write_tool  = tools[1]

    researcher = Agent(role="Research Analyst",   goal="Collect and organize the latest information", backstory=RESEARCHER_SYSTEM_PROMPT, tools=[search_tool], verbose=True)
    analyst    = Agent(role="Data Analyst",       goal="Extract insights from collected information", backstory=ANALYST_SYSTEM_PROMPT,   tools=[],           verbose=True)
    reporter   = Agent(role="Report Writer",      goal="Write analysis results as a markdown report", backstory=REPORTER_SYSTEM_PROMPT,  tools=[write_tool], verbose=True)

    research_task  = Task(description="Search for 5 recent news articles on the topic '{topic}' and organize them.", expected_output="List of news articles", agent=researcher)
    analysis_task  = Task(description="Extract 3 key insights and trends from the collected news.", expected_output="List of insights", agent=analyst, context=[research_task])
    report_task    = Task(description="Write the analysis results as a markdown report and save it to 'report.md'.", expected_output="Markdown report file", agent=reporter, context=[research_task, analysis_task])

    return Crew(agents=[researcher, analyst, reporter], tasks=[research_task, analysis_task, report_task], process=Process.sequential, verbose=True)
