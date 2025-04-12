from dotenv import load_dotenv
from google.adk import Agent

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# from google.adk.sessions import InMemorySessionService
# from google.genai import types

load_dotenv()
# APP_NAME = "university_app"
# USER_ID = "dev_user_01"
# SESSION_ID = "pipeline_session_01"

model = LiteLlm(model="openai/gpt-4o")
coordinator_prompt = """
You are an coordinator in a university. You have access to maths and physics teacher.
You help route student's question to the appropriate expert based on the nature of the 
question.
"""

maths_prompt = """
You are an expert maths teacher. You can only answer questions related to maths
"""

physics_prompt = """
You are an expert physics teacher. You can only answer questions related to physics
"""

maths_agent = LlmAgent(model=model,
                       instruction=maths_prompt,
                       description="helps answer maths question",
                       name="maths_agent"
                       )

physics_agent = LlmAgent(model=model,
                         instruction=physics_prompt,
                         description="helps answer physics question",
                         name="physics_agent"
                         )
root_agent = Agent(model=model,
                   description="helps route question to the right expert",
                   instruction=coordinator_prompt,
                   name="coordinator_agent",
                   sub_agents=[
                       maths_agent,
                       physics_agent
                   ])

# session_service = InMemorySessionService()
# session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# runner = Runner(agent=coordinator, app_name=APP_NAME, session_service=session_service)
#
#
# # Agent Interaction
# def call_agent(query):
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
#
#     for event in events:
#         if event.is_final_response():
#             final_response = event.content.parts[0].text
#             print("Agent Response: ", final_response)
#
#
# call_agent("add 2 and 3")
