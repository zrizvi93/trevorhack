# 🦙📚 TrevorText - Copilot-augmented

Empower Trevor Project counselors with RAG-assisted TrevorText, an AI co-pilot powered by LlamaIndex to help counselors focus on people, not paperwork. Link to Hackathon Submission: https://devpost.com/software/counselor-copilot

In this version, we artificially simulate the contact's responses. The extension would be to integrate the tool with the existing SalesForce CRM and webchat platform used by the Trevor Project.

## Local Dev Loop

`pyenv local`
Use python version in .python-version file


`virtualenv -v venv-trevorhack-streamlit && source venv-trevorhack-streamlit/bin/activate`
Create and activate virtual environment



Create environment variable file with: `touch .env` and add the following variables ([Reference](https://docs.datastax.com/en/astra/astra-db-vector/integrations/llamaindex.html))
```
ASTRA_DB_APPLICATION_TOKEN="TOKEN"
ASTRA_DB_API_ENDPOINT="API_ENDPOINT"
OPENAI_API_KEY="API_KEY"
```

`pip install -r requirements.txt`
Install deps


`streamlit run streamlit_app.py`
Run app from the project root


The dev server can be accessed at [localhost:8501](http://localhost:8501/)


Additional Notes:

`kill -9 $(lsof -i:8501 -t) 2> /dev/null`
To quickly kill any process running on port 8501


## Overview of the App

<img src="app.png" width="75%">

- Takes user queries via Streamlit's `st.chat_input` and displays both user queries and model responses with `st.chat_message`
- Uses LlamaIndex to load and index data and create a chat engine that will retrieve context from that data to respond to each user query
- Copilot Agent takes actions using provided tools to search the web for resources, escalate cases, and retrieve relevant documents to inform recommended responses.

## Demo App

TBC

## Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:
1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.

## Try it out

Once the app is loaded, enter your OpenAI API key (please forgive the ghost elements) and check out the suggested responses from the agent.

Edit `data/library/demo_conversation_client.txt` to try out responses to different statements.
