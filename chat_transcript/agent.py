from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field


class ChatTranscript(BaseModel):
    meeting_notes: str = Field(description="Important notes from the transcript")
    action_items: str = Field(description="All the action items from the transcript")


load_dotenv()
model = "openai/gpt-4.1"
model_abstraction = LiteLlm(model=model)

note_extractor_agent = LlmAgent(
    name="notes_extractor",
    model=model_abstraction,
    instruction="""You are an excellent meeting note extractor. Please extract the meeting minutes  from provided 
    chat transcript.Given a transcript, respond ONLY with a JSON object containing the meeting notes and action 
    items. DO NOT ADD ANYTHING ELSE.Format: {"meeting_notes": "meeting_notes","action_items":"action_items"}""",
    output_schema=ChatTranscript,  # Enforce JSON output
    output_key="meeting_minutes"  # Store result in state['found_capital']
    # Cannot use tools=[get_capital_city] effectively here
)

root_agent = note_extractor_agent
