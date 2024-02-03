# 🦙📚 LlamaIndex - Chat with the Streamlit docs

Build a chatbot powered by LlamaIndex that augments GPT 3.5 with the contents of the Streamlit docs (or your own data).

## Local Dev Loop

`pyenv local`
Use python version in .python-version file


`virtualenv -v venv-trevorhack-streamlit && source venv-trevorhack-streamlit/bin/activate`
Create and activate virtual environment


`mkdir .streamlit && cd .streamlit && touch secrets.toml`
Create secrets file 


openai_key = "XXXX"
insert your API key for open ai / others like so


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

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://llamaindex-chat-with-docs.streamlit.app/)

## Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:
1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.

## Try out the app

Once the app is loaded, enter your question about the Streamlit library and wait for a response.
