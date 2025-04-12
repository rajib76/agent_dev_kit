from datetime import datetime

from google.adk.events import Event
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, UserContent, Part

# Let us create a session to understand its structure
# Think about session object is a container that holds every information related to a specific chat thread
# It has four distinct sections
# A section that uniquely identifies the conversation
# A section that can store the chronology of interactions
# A section that can act as the scratchpad of the current conversation
# A section that tracks the timestamp for an event in the conversation thread


# Create a simple session to examine its properties
temp_service = InMemorySessionService()

example_session: Session = temp_service.create_session(
    app_name="my_app",
    user_id="example_user",
    state={"initial_key": "initial_value"}  # State can be initialized
)

print(f"--- Examining Session Properties ---")
print(f"ID (`id`):                {example_session.id}")
print(f"Application Name (`app_name`): {example_session.app_name}")
print(f"User ID (`user_id`):         {example_session.user_id}")
print(f"State (`state`):           {example_session.state}")  # Note: Only shows initial state here
print(f"Events (`events`):         {example_session.events}")  # Initially empty
print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
print(f"---------------------------------")

# Let's now examine the session service component
# Core responsibilities of the service include
# Start a new conversation : it allows to create a session as we saw above
# Resuming an existing conversation: Can retrieve a specific session so the agentic system can pause and resume
# Saving the state and progress of the conversation: appends the interactions, ideally building the episode of the chat
# List conversation: Finds the active sessioj threads for a user and application
# Clean up : Deleting the session obejct when the conversation no longer needs it

# ADK provides three types of session service, which I will cover separately
# InMemorySessionService
# DatabaseSessionService
# VertexAiSessionService

ev1 = Event(
    invocation_id ="in0001",
    author = "rajib",
    actions ={},
    long_running_tool_ids=None,
    branch=None,
    id="ev01",
    timestamp=datetime.now().timestamp()
)
content = UserContent(Part.from_uri(file_uri="gs://bucket/file.txt", mime_type="text/plain"))
ev1.content=content

temp_service.append_event(session=example_session, event=ev1)

ev2 = Event(
    invocation_id ="in0001",
    author = "rajib",
    actions ={},
    long_running_tool_ids=None,
    branch=None,
    id="ev02",
    timestamp=datetime.now().timestamp()
)

content = UserContent("Why is the sky blue?")
ev2.content=content
temp_service.append_event(session=example_session, event=ev2)

events = example_session.events

for event in events:
    print(f"Events (`event`):         {event}")  # now lets see

session = temp_service.list_sessions(app_name=example_session.app_name, user_id=example_session.user_id)
print(f"Sessions (`session`): , {session}")

# Clean up (optional for this example)
temp_service.delete_session(app_name=example_session.app_name,
                            user_id=example_session.user_id, session_id=example_session.id)

session = temp_service.list_sessions(app_name=example_session.app_name, user_id=example_session.user_id)
print(f"Sessions after deletion (`session`): , {session}")
