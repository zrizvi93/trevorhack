import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

# Client conversation idx initialization
if 'script_idx' not in st.session_state:
    st.session_state.script_idx = 1
    
st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("TrevorText")
# st.info("Check out the full tutorial to build this app in our [blog post](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/)", icon="📃")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "user", "content": "Hi, welcome to TrevorText. What's going on?"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

col1, col2, col3 = st.columns([0.4, 0.3, 0.3], gap="small")

with col1:
    if "chat_engine" not in st.session_state.keys():   # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
    if prompt := st.chat_input("Your question"):   # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

with col2:
    with st.container(height=570):
        age = st.number_input("Age", value=0)
        city = st.text_input("City")
        state = st.text_input("State")
        suicidal_bool = st.checkbox("Are they thinking of killing themselves?")
        summary = st.text_area("Brief summary/ Narrative")
        risk_level = st.selectbox("Risk Level", ["Not Suicidal", "Low Risk", "Medium Risk", "High Risk", "Imminent Risk"])
    st.subheader("Reply Suggestions")


with col3:
    with st.container(height=190):
        name = st.text_input("First Name")
        primary_issue = st.text_input("Primary Issue")


for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

client_script = open("data/library/demo_conversation_client.txt", "r").readlines()

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = "sorry"
        if st.session_state.script_idx < len(client_script):
            response = client_script[st.session_state.script_idx][2:]
        st.session_state.script_idx += 2 
        st.write(response)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message) # Add response to message history
