# Step 3: Create agent
import asyncio
from typing import Any

from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import DatabaseSessionService
from google.adk.tools import LongRunningFunctionTool
from google.genai import types

load_dotenv()

# 1. Setting up the session
APP_NAME = "demo_app"
USER_ID = "user1"
SESSION_ID = "session1"
db_url = "sqlite:///./my_agent_data.sqlite"
session_service = DatabaseSessionService(db_url=db_url)
session = session_service.get_session(app_name=APP_NAME,
                                      user_id=USER_ID,
                                      session_id=SESSION_ID)

# 2. Setting up the model
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_GPT_4O_LITE_LLM = LiteLlm(model=MODEL_GPT_4O)


# 3. Setting up the tool
def ask_for_manager(task: str) -> dict[str, Any]:
    return {
        'status': "PENDING",
        'task': task,
        'manager': 'Taylor',
        'ticket_id': 'task-123'
    }


def get_request_status():
    return {
        'status': "APPROVED",
        'ticket_id': 'task-123'
    }


# 4. Wrapping it up with LongRunningFunctionTool
approval_tool = LongRunningFunctionTool(func=ask_for_manager)

# 5. Setting up the agent
agent = Agent(
    model=MODEL_GPT_4O_LITE_LLM,
    name="approval_agent",
    instruction="Ask manager approval for any important task using the tool",
    tools=[approval_tool]
)

# 6. Setting uo the runner
runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)


async def follow_up():
    for event in session.events:
        tool_ids = event.long_running_tool_ids
        if tool_ids:
            parts = event.content.parts
            print(parts)
            for part in parts:
                if part.function_call:
                    print(part.function_call.id)
                    print(part.function_call.name)
                    approved_response = types.FunctionResponse(
                        id=part.function_call.id,
                        name=part.function_call.name,
                        response=get_request_status()
                    )
                    follow_up = types.Content(
                        role='user',
                        parts=[types.Part(function_response=approved_response)]
                    )
                    events = runner.run_async(session_id=SESSION_ID, user_id=USER_ID, new_message=follow_up)
                    async for event in events:
                        if event.content:
                            for part in event.content.parts:
                                if part.text:
                                    print(f"[{event.author}]: {part.text}")


asyncio.run(follow_up())
