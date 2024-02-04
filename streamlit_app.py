import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
import time


# Client conversation idx initialization
client_script = open("data/library/demo_conversation_client.txt", "r").readlines()
if 'script_idx' not in st.session_state:
    st.session_state.script_idx = 1

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Welcome to TrevorText, powered by LlamaIndex 💬🦙")

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading"):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

tab1, tab2 = st.tabs(["Crisis Hotline Chat", "Case Form"])

# crisis intervention room tab
with tab1:
    col_a1, col_a2 = st.columns([0.5, 0.5], gap="small")
    with col_a1:
        if "messages" not in st.session_state.keys(): # Initialize the chat messages history
            st.session_state.messages = [
                {"role": "user", "content": "Hi, welcome to TrevorText. What's going on?"}
        ]

        for message in st.session_state.messages:   # Display the prior chat messages
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
        if "chat_engine" not in st.session_state.keys():   # Initialize the chat engine
            st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
        if prompt := st.chat_input("Your question"):   # Prompt for user input and save to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

        # If last message is not from assistant, generate a new response
        if st.session_state.messages[-1]["role"] != "assistant":
            time.sleep(2) 
            with st.chat_message("assistant"):
                if st.session_state.script_idx < len(client_script):
                    response = client_script[st.session_state.script_idx][2:]
                    st.session_state.script_idx += 2 
                    st.write(response)
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message) # Add response to message history
                else:
                    st.info("Contact has left the chat")

        print(st.session_state.messages)
        
        with col_a2:
            st.subheader("Suggested Reply")
            st.info("Have you been feeling overwhelmed or hopeless?")
            st.subheader("Sources")

            source_file_names = ["README.md", "HelloWorld.py", "GirlPowerPlusTarun.pdf"]
            source_links = []
            base_link = "https://github.com/zrizvi93/trevorhack/tree/main/data/{}"
            for file in source_file_names:
                source_links.append(base_link.format(file))

            i = 0
            sources_row = st.columns(3)
            for col in sources_row:
                with col.container(height=50):
                    st.markdown(f'<a href="{source_links[i]}" target="_blank">"{source_file_names[i]}"</a>', unsafe_allow_html=True)
                i += 1

            st.subheader("Additional Research")
            st.write('''
            <div style="width: 100%; padding-top: 70%; position: relative;">
                <iframe src="https://www.perplexity.ai/" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
            </div>''', unsafe_allow_html=True)

