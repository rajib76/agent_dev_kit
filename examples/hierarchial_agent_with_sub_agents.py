# Based on the documentation available here
# https://google.github.io/adk-docs/agents/multi-agents/#2-adk-primitives-for-agent-composition

import asyncio

from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()
MODEL_GPT_4O = "openai/gpt-4o"

MODEL_GPT_4O_LITE_LLM = LiteLlm(model=MODEL_GPT_4O)

# Define constants for identifying the interaction context
APP_NAME = "tutor_app"
USER_ID = "user_1"
SESSION_ID = "session_001"  # Using a fixed ID for simplicity

session_service = InMemorySessionService()

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
math_agent = LlmAgent(name="Math",
                      description="Handles math question",
                      model=MODEL_GPT_4O_LITE_LLM,
                      instruction="You answer only math questions")

physics_agent = LlmAgent(name="Physics",
                         description="Handles physics question",
                         model=MODEL_GPT_4O_LITE_LLM,
                         instruction="You answer only physics questions")

coordinator = LlmAgent(
    name="TutorCoordinator",
    model=MODEL_GPT_4O_LITE_LLM,
    instruction="Route user requests: Use Math agent for math questions, physics agent for physics questions.",
    description="Main tutor router.",
    # allow_transfer=True is often implicit with sub_agents in AutoFlow
    sub_agents=[math_agent, physics_agent]
)

# parent_agent = coordinator.parent_agent
parent_agent = coordinator.root_agent.parent_agent

print("Parent Agent is ", parent_agent)

sub_agents = coordinator.sub_agents

print("Sub agents are ", sub_agents)

runner = Runner(
    agent=coordinator,
    app_name=APP_NAME,
    session_service=session_service
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

    return final_response_text


async def run_conversation():
    result = await call_agent_async("What is pythagoras theorem and what is refraction?",
                                    runner=runner,
                                    user_id=USER_ID,
                                    session_id=SESSION_ID)

    return result

result = asyncio.run(run_conversation())
#
print("final result ", result)
