# --- 1. Imports and Setup ---
import os
import asyncio
from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    AgentOutput,
    ToolCall,
    ToolCallResult,
)
from llama_index.core.workflow import Context
from google.genai import types as google_types

# --- 2. Load Environment Variables ---
# Load variables from a .env file in the same directory
load_dotenv()

# This script loads the Google API key from an environment variable.
# Ensure you have a .env file with: GOOGLE_API_KEY="YOUR_API_KEY_HERE"
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY not found. Please create a .env file and set your API key."
    )

# --- 3. Setup LLMs ---
# Using Gemini model.
# The LlamaIndex library automatically uses the GOOGLE_API_KEY environment variable.
llm = GoogleGenAI(model="gemini-2.5-pro")

# This specialized LLM is equipped with a built-in Google Search tool.
# It will be used exclusively by the search_web tool function.
Google Search_tool = google_types.Tool(Google Search=google_types.GoogleSearch())
llm_with_search = GoogleGenAI(
    model="gemini-2.5-pro",
    generation_config=google_types.GenerateContentConfig(tools=[Google Search_tool])
)

# --- 4. Define Tools (with state management) ---

# This tool function uses the search-enabled LLM to research a topic.
async def search_web(ctx: Context, query: str) -> str:
    """Useful for searching the web about a specific query or topic"""
    print(f"--- Performing web search for: '{query}' ---")
    response = await llm_with_search.acomplete(
        f"Please research given this query or topic, and return the result\n<query_or_topic>{query}</query_or_topic>"
    )
    return str(response)

# Use the 'edit_state' context manager for safe, reliable state updates.
async def record_notes(ctx: Context, notes: str, notes_title: str) -> str:
    """Useful for recording notes on a given topic."""
    print(f"--- Recording notes titled: '{notes_title}' ---")
    async with ctx.store.edit_state() as ctx_state:
        if "research_notes" not in ctx_state["state"]:
            ctx_state["state"]["research_notes"] = {}
        ctx_state["state"]["research_notes"][notes_title] = notes
    return "Notes recorded."

async def write_report(ctx: Context, report_content: str) -> str:
    """Useful for writing a report on a given topic."""
    print("--- Writing report ---")
    async with ctx.store.edit_state() as ctx_state:
        ctx_state["state"]["report_content"] = report_content
    return "Report written."

async def review_report(ctx: Context, review: str) -> str:
    """Useful for reviewing a report and providing feedback."""
    print("--- Reviewing report ---")
    async with ctx.store.edit_state() as ctx_state:
        ctx_state["state"]["review"] = review
    return "Report reviewed."

# --- 5. Define the Agents ---
# Using strong, explicit system prompts helps guide the agent's behavior correctly.
research_agent = FunctionAgent(
    name="ResearchAgent",
    description="Useful for searching the web for information and recording notes.",
    system_prompt=(
        "Your ONLY job is to research topics using your tools and record detailed notes. "
        "You MUST NOT write the final report. You are forbidden from generating final content. "
        "First, use your tools to find information. Second, record that information as notes. "
        "Once you have sufficient notes, you MUST hand off control to the 'WriteAgent'."
    ),
    llm=llm,
    tools=[search_web, record_notes],
    can_handoff_to=["WriteAgent"],
)

write_agent = FunctionAgent(
    name="WriteAgent",
    description="Useful for writing a report on a given topic.",
    system_prompt=(
        "You are the WriteAgent. Your job is to write a report in markdown format "
        "based *only* on the provided research notes. Once done, hand off to the ReviewAgent."
    ),
    llm=llm,
    tools=[write_report],
    can_handoff_to=["ReviewAgent", "ResearchAgent"],
)

review_agent = FunctionAgent(
    name="ReviewAgent",
    description="Useful for reviewing a report and providing feedback.",
    system_prompt=(
        "You are the ReviewAgent. Review the report and provide feedback. "
        "Approve it or request changes and hand off back to the WriteAgent if necessary."
    ),
    llm=llm,
    tools=[review_report],
    can_handoff_to=["ResearchAgent", "WriteAgent"],
)

# --- 6. Create the Workflow ---
agent_workflow = AgentWorkflow(
    agents=[research_agent, write_agent, review_agent],
    root_agent=research_agent.name,
    initial_state={
        "research_notes": {},
        "report_content": "Not written yet.",
        "review": "Review required.",
    },
)

client_requirements = """
Write a Product Requirement Document (PRD) for a mobile application for a real-time translation service.
The PRD should cover key features like voice-to-text, text-to-speech, and offline mode.
Start by researching best practices for a user-friendly interface in a translation app.
"""

# --- 7. Execute the workflow and stream events ---
async def run_workflow():
    """Initializes and runs the agent workflow, printing events as they occur."""
    handler = agent_workflow.run(user_msg=client_requirements)
    current_agent = None

    async for event in handler.stream_events():
        if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
            current_agent = event.current_agent_name
            print(f"\n{'='*50}\n🤖 Agent: {current_agent}\n{'='*50}\n")
        elif isinstance(event, AgentOutput):
            if event.response.content:
                print("📤 Output:", event.response.content)
            if event.tool_calls:
                print("🛠️ Planning to use tools:", [call.tool_name for call in event.tool_calls])
        elif isinstance(event, ToolCallResult):
            print(f"🔧 Tool Result ({event.tool_name}):")
            # Truncate long tool outputs for cleaner logs.
            print(f"    Output: {str(event.tool_output)[:300]}...")
        elif isinstance(event, ToolCall):
            # Don't print the handoff tool calls for cleaner output.
            if "handoff" not in event.tool_name:
                print(f"🔨 Calling Tool: {event.tool_name}")
                print(f"    With arguments: {event.tool_kwargs}")

    print("\n--- ✅ Workflow Complete ---")
    state = await handler.ctx.store.get("state")
    print("\n--- Final Report Content ---\n")
    print(state["report_content"])
    print("\n----------------------------\n")
    print("\n--- Final Review ---\n")
    print(state["review"])

# --- 8. Run the main asynchronous function ---
# This entry point is used when running the script from the command line.
if __name__ == "__main__":
    asyncio.run(run_workflow())
