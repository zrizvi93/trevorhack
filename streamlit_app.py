import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
import time
from llama_index.tools import FunctionTool
from llama_index.agent import ReActAgent
from llama_index.agent import OpenAIAgent
import helpers
from llama_index.tools.tool_spec.load_and_search.base import LoadAndSearchToolSpec
from llama_hub.tools.google_search.base import GoogleSearchToolSpec
import emails

# Client conversation idx initialization
client_script = open("data/library/demo_conversation_client.txt", "r").readlines()
if 'script_idx' not in st.session_state:
    st.session_state.script_idx = 1

if 'custom_chat_input' not in st.session_state:
    st.session_state.custom_chat_input = ''  # Initialize it with an empty string

if 'autopopulation' not in st.session_state:
    st.session_state.autopopulation = False

if 'suggested_reply1' not in st.session_state:
    st.session_state.suggested_reply1 = ""

st.set_page_config(page_title="TrevorText, powered by LlamaIndex", page_icon="🦙", layout="wide", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Welcome to TrevorText, powered by LlamaIndex 💬🦙")

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading"):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4", temperature=0, system_prompt="You are an expert and sensitive mental health copilot assistant for a mental health counselor. Your job is to help the counselor by providing suggestions based on reference documents."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

@st.cache_resource(show_spinner=False)
def build_agent():
    agent = ReActAgent.from_tools([search_tool, escalate_tool, resource_tool], llm=OpenAI(model="gpt-4"), verbose=True)
    return agent

def escalate() -> None:
    """Recognizes a high-risk statement from the mental health chatbot and escalates to the next level of management. High-risk is defined as a statement that suggests that the client has a plan, means, and intent to harm oneself or others (specific details on when, where, and how)."""
    st.error("High risk detected. Please consider escalating immediately.", icon="🚨")

def get_resource_for_response(user_input) -> str:
    """Recognizes a no, low- or medium-risk statement from the mental health chatbot, seeks resources to inform potential chat responses"""
    response = st.session_state.query_engine.retrieve(user_input)
    resources = [t.node.metadata["file_name"] for t in response]
    content = [t.node.text for t in response]
    result = dict(zip(resources, content))
    return result

def search_for_therapists(locality: str = "Houston, Texas") -> str:
    """Use the Google Search Tool but only specifically to find therapists in the client's area, then send email to update the client with the results."""
    google_spec = GoogleSearchToolSpec(key=st.secrets.google_search_api_key, engine=st.secrets.google_search_engine)
    tools = LoadAndSearchToolSpec.from_defaults(google_spec.to_tool_list()[0],).to_tool_list()
    agent = OpenAIAgent.from_tools(tools, verbose=True)
    response = agent.chat(f"what are the names of three specific therapists in {locality}?")
    message = emails.html(
        html=f"<p>Hi Kris.<br>{response}</p>",
        subject="Helpful resources from TrevorChat",
        mail_from=('TrevorChat Counselor', 'contact@mychesscamp.com')
    )
    smtp_options = {
        "host": "smtp.gmail.com", 
        "port": 587,
        "user": "contact@mychesscamp.com",
        "password": "Fiverkids123@@##$$",   
        "tls": True
    }
    response = message.send(to='kris.rocks.socks@gmail.com', smtp=smtp_options)
    return response

def get_counselor_resources(response) -> list:
    output = ['cheatsheet_empathetic_language.txt', 'cheatsheet_maintaining_rapport.txt', 'cheatsheet_risk_assessment.txt']
    try:
        raw_output = response.sources[0].raw_output
        output_dict = dict(raw_output)
        output = [key for key in output_dict.keys()]
    except Exception as e: # Hard-coded draft return
        print(str(e))
        return output
    return output

def get_modified_prompt(user_input) -> str:
    return f"""You are a helpful mental health assistant chatbot, helping to train a junior counselor by providing suggestions on responses to client chat inputs. What would you recommend that the consider could say if someone says or asks '{user_input}'?
    """

def send_chat_message():
    if st.session_state.custom_chat_input:  # Check if the input is not empty
        st.session_state.messages.append({"role": "user", "content": st.session_state.custom_chat_input})
        st.session_state.custom_chat_input = ""

def set_custom_chat_input():
    st.session_state.custom_chat_input = st.session_state.suggested_reply1

def get_form_value_from_convo(convo, form_value) -> str:
    return f"""You are a helpful assistant filling out a form. Extract the person's {form_value} from the following converstation in to input into the form. {convo}"""

def get_int_value_from_convo(convo, form_value) -> str:
    return f"""You are a helpful assistant filling out a form. Extract the person's {form_value} from the following converstation in to input into the form. {convo}"""

def get_risk_value_from_convo(convo) -> str:
    return f"""You are a helpful assistant filling out a form. Reply 0 if the person does not seem at risk based on the conversation. {convo}"""

search_tool = FunctionTool.from_defaults(fn=search_for_therapists)
escalate_tool = FunctionTool.from_defaults(fn=escalate)
resource_tool = FunctionTool.from_defaults(fn=get_resource_for_response)
index = load_data()
agent = build_agent()

if "query_engine" not in st.session_state.keys():
    st.session_state.query_engine = index.as_query_engine(similarity_top_k=3, verbose=True)

tab1, tab2 = st.tabs(["Crisis Hotline Chat", "Case Form"])

# crisis intervention room tab
with tab1:
    col_a1, col_a2 = st.columns([0.5, 0.5], gap="small")
    with col_a1:
        if "chat_engine" not in st.session_state.keys():   # Initialize the chat engine
            st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

        if "messages" not in st.session_state.keys():  # Initialize the chat messages history
            st.session_state.messages = [
                {"role": "user", "content": "Hi, welcome to TrevorText. What's going on?"}
            ]

        for message in st.session_state.messages:   # Display the prior chat messages
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # If last message is not from assistant, generate a new response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                if st.session_state.script_idx < len(client_script):
                    response = client_script[st.session_state.script_idx][2:]
                    st.session_state.script_idx += 2
                    st.write(response)
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message)  # Add response to message history
                else:
                    st.info("Contact has left the chat")
                    with st.status("Autopoulating form...", expanded=True) as status:
                        st.write("Downloading chat history...")
                        chathistory = ""
                        for item in st.session_state.messages:
                            chathistory += item['content'] + '\n'
                        print(chathistory)
                        time.sleep(1) 
                        st.write("Analyzing chat...")

                        nameVal = agent.chat(get_form_value_from_convo(chathistory, "First Name"))
                        issueVal = agent.chat(get_form_value_from_convo(chathistory, "Primary Issue"))
                        ageVal = agent.chat(get_int_value_from_convo(chathistory, "Age"))
                        cityVal = agent.chat(get_form_value_from_convo(chathistory, "City"))
                        stateval = agent.chat(get_form_value_from_convo(chathistory, "State"))
                        summaryVal = agent.chat(get_form_value_from_convo(chathistory, "Brief summary/ Narrative"))

                        immenentriskBool = agent.chat(get_risk_value_from_convo(chathistory))
                        riskBool = agent.chat(get_risk_value_from_convo(chathistory))
                        
                        # nameVal = "Kris"
                        # issueVal = "Coming out to parents"
                        # ageVal = 24
                        # cityVal = "Sugarland"
                        # stateval = "TX"
                        # immenentriskBool = 0
                        # summaryVal = "Anxiety around coming out to parents. Needs LGBTQ guidance and support"
                        # riskBool = 0 
                        st.write("Populating form...")
                        # 3. fill out form

                        # case form tab
                        with tab2:
                            col_b1, col_b2 = st.columns([0.5, 0.5], gap="small")
                            with col_b1:
                                with st.container(height=190):
                                    name = st.text_input("First Name", value=nameVal)
                                    primary_issue = st.text_input("Primary Issue", value=issueVal)
                            with col_b2:
                                with st.container(height=570):
                                    age = st.number_input("Age", value=int(str(ageVal)))
                                    city = st.text_input("City", value=cityVal)
                                    state = st.text_input("State", value=stateval)
                                    print("immenentriskBool", immenentriskBool)
                                    imminent_risk_bool = st.selectbox("Are they thinking of killing themselves?", ["No", "Yes"], index=int(str(immenentriskBool)))
                                    summary = st.text_area("Brief summary/ Narrative", value=summaryVal)
                                    print("riskBool", riskBool)
                                    risk_level = st.selectbox("Risk Level", ["Not Suicidal", "Low Risk", "Medium Risk", "High Risk", "Imminent Risk"], index=int(str(riskBool)))
                        status.update(label="Case Form filled out! Please double check all values", state="complete", expanded=False)
                        st.session_state.autopopulation = True

        # Send message in Chat
        with st.form("chat_form"):
            custom_chat_input = st.text_area("Your reply", key="custom_chat_input")
            _, right_justified_button_col = st.columns([0.8, 0.15])   # Adjust the ratio as needed
            with right_justified_button_col:
                submit_button = st.form_submit_button("Send :incoming_envelope:", on_click=send_chat_message)

    with col_a2:
        st.subheader("Contact Overview")
        if len(st.session_state.messages) > 1:
            st.write(helpers.CLIENT_SUMMARY)

        st.subheader("Suggested Reply")
        suggested_reply = ""
        source_file_names = ['cheatsheet_empathetic_language.txt', 'cheatsheet_maintaining_rapport.txt', 'cheatsheet_risk_assessment.txt']
        if st.session_state.messages[-1]["role"] == "assistant": 
            response = agent.chat(get_modified_prompt(st.session_state.messages[-1]["content"])) 
            suggested_reply = str(response)
            suggested_reply = suggested_reply.split('"')[1] if '"' in suggested_reply else suggested_reply
            st.session_state.suggested_reply1 = suggested_reply  # Store the suggested reply in the session state
            st.info(suggested_reply)
            source_file_names = get_counselor_resources(response)

        # Add a button to populate the custom input field with the suggested reply
        if st.button("Use Suggested Reply", on_click=set_custom_chat_input):
            pass

        st.subheader("Sources")
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

