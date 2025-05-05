from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm

from parallel_agent.transcript import TranscriptRetriever

load_dotenv()
model = "openai/gpt-4o"
model_abstraction = LiteLlm(model=model)
transcript_retriever = TranscriptRetriever()

meeting_transcript = transcript_retriever.get_transcript()

meeting_notes_agent = LlmAgent(
    name="NotesCreator",
    description="Creates notes from an meeting transcript",
    instruction=f"""
    You are an expert notes extractor. You will extract only the key discussion highlights from a given meeting transcript. 
    Here is the transcript for you.
    {meeting_transcript}
    """,
    output_key="notes_output",
    model=model_abstraction

)

action_item_agent = LlmAgent(
    name="ActionItemCreator",
    description="Creates action items from a meeting transcript",
    instruction=f"""
    You are an expert action item extractor. You will extract only the action items from a given meeting transcript. 
    Here is the transcript for you.
    {meeting_transcript}
    """,
    output_key="notes_output",
    model=model_abstraction

)

meeting_summary_agency = ParallelAgent(
    name = "MeetingSummarizationWorkflow",
    sub_agents=[meeting_notes_agent,action_item_agent],
    description="Leverages multiple agents to create a minutes of meeting with notes and action items"

)

root_agent = meeting_summary_agency