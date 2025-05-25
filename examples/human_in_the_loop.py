import asyncio
from typing import Any

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.events import Event
from google.genai import types

load_dotenv()

# 1. Setting up of the session details
APP_NAME = "demo_app"
USER_ID = "user1"
SESSION_ID = "session1"

db_url = "sqlite:///./my_agent_data.sqlite"

session_service = DatabaseSessionService(db_url=db_url)
session = session_service.create_session(app_name=APP_NAME,
                                         user_id=USER_ID,
                                         session_id=SESSION_ID)

# 2 Setting up the model
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_GPT_4O_LITE_LLM = LiteLlm(model=MODEL_GPT_4O)


# 3. Defining the tool for getting human approval
def ask_for_manager(task: str) -> dict[str, Any]:
    status = "PENDING"
    return {
        'status': status,
        'task': task,
        'manager': 'Taylor',
        'ticket_id': 'task-123'
    }


# 4. Wrap the tool with LongRunningFunctionTool
approval_tool = LongRunningFunctionTool(func=ask_for_manager)

# 5. Setting up the agent
agent = Agent(
    model=MODEL_GPT_4O_LITE_LLM,
    name="approval_agent",
    instruction="Ask manager approval for any important task using the tool. Output only APPROVED or PENDING",
    tools=[approval_tool],
    output_key="review_status"
)

# 6. Setting up the runner
runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)


# 7. interact with the agent
async def interact(query: str):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(session_id=SESSION_ID, user_id=USER_ID, new_message=content)
    async for event in events:
        if event.content:
            for part in event.content.parts:
                if part.function_response:
                    print(f"function response : {part.function_response}")
                if part.text:
                    print(f"[{event.author}]: {part.text}")


asyncio.run(interact("Please ask the manager to approve quarterly review, till then keep the status as pending"))
