import asyncio
import os

from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types
load_dotenv()

session_service = InMemorySessionService()
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_GPT_4O_LITE_LLM = LiteLlm(model=MODEL_GPT_4O)

instruction_prompt = """
You will add two numbers using a math addition tool
"""

# Define constants for identifying the interaction context
APP_NAME = "math_app"
USER_ID = "user_1"
SESSION_ID = "session_001"  # Using a fixed ID for simplicity

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)


async def add(
        num_1: int,
        num_2: int
) :
    """Tool to call database (nl2sql) agent."""
    result = num_1 + num_2
    return result


math_agent = Agent(
    model=MODEL_GPT_4O_LITE_LLM,
    name="math_agent",
    instruction=instruction_prompt,
    global_instruction="",
    sub_agents=[],
    tools=[
        add
    ],
)

runner = Runner(
    agent=math_agent,  # The agent we want to run
    app_name=APP_NAME,  # Associates runs with our app
    session_service=session_service  # Uses our session manager
)

async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            print("final event ", event.is_final_response())
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")


# @title Run the Initial Conversation

# We need an async function to await our interaction helper
async def run_conversation():
    await call_agent_async("What is the sum of 2 and 3",
                           runner=runner,
                           user_id=USER_ID,
                           session_id=SESSION_ID)

asyncio.run(run_conversation())

