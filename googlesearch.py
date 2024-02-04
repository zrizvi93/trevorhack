# Setup OpenAI Agent
import openai

openai.api_key = "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"
from llama_index.agent import OpenAIAgent

# Import and initialize our tool spec
from llama_index.tools.tool_spec.load_and_search.base import LoadAndSearchToolSpec
from llama_hub.tools.google_search.base import GoogleSearchToolSpec

google_spec = GoogleSearchToolSpec(key="AIzaSyDI6KxWdW4Po5zdjvTmCFC1CX9RRP51YkY", engine="b409afba29b3742a2")

# Wrap the google search tool as it returns large payloads
tools = LoadAndSearchToolSpec.from_defaults(
    google_spec.to_tool_list()[0],
).to_tool_list()

# Create the Agent with our tools
agent = OpenAIAgent.from_tools(tools, verbose=True)
agent_response = agent.chat("what are the names of three good therapists in San Francisco")
print(agent_response)