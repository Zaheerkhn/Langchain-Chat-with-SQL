import os
import sqlite3
import streamlit as st 
from dotenv import load_dotenv
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain_groq import ChatGroq

# Load environment variables
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Langchain: Chat with SQL"
groq_api = os.getenv("GROQ_API_KEY")
mysql_host = st.secrets["MYSQL_HOST"]
mysql_user = st.secrets["MYSQL_USER"]
mysql_password = st.secrets["MYSQL_PASSWORD"]
mysql_database = st.secrets["MYSQL_DATABASE"]

# --- Custom CSS for Dark Chat Styling ---
st.markdown("""
    <style>
        /* Custom Chat Bubbles */
        .chat-message {
            padding: 12px;
            border-radius: 8px;
            margin: 5px 0;
            color: white;
            font-weight: 500;
        }
        .user-message {
            background-color: #003366;  /* Dark Blue */
            text-align: right;
        }
        .assistant-message {
            background-color: #FF7F50;  /* Coral Orange */
            text-align: left;
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            color: white;
        }
        /* Chat Input Box */
        input[type="text"] {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 🌟 Page Title ---
st.title("🤖 Langchain: Chat with SQL")

# Database Selection
st.sidebar.subheader("📂 Database Connection")
db_options = ["Select Local Database (Students.db)", "Select MySQL Database"]
selected_db = st.sidebar.radio("Choose a database:", db_options, index=0)

# --- 🛠 Database Configuration ---
LOCALDB = "USE_LOCAL_DB"
MYSQL = "USE_MYSQL"

if selected_db == "Select MySQL Database":
    db_uri = MYSQL
    with st.sidebar.expander("🔧 MySQL Configuration"):
        mysql_host = st.text_input("MySQL Host")
        mysql_user = st.text_input("MySQL User")
        mysql_password = st.text_input("MySQL Password", type="password")
        mysql_database = st.text_input("MySQL Database")
else:
    db_uri = LOCALDB

# Error Handling for Database Selection
if not db_uri:
    st.error("⚠️ Please select a database and provide necessary details.")

# --- 🤖 Initialize LLM ---
llm = ChatGroq(groq_api_key=groq_api, model_name="Llama-3.3-70b-Versatile", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None):
    if db_uri == LOCALDB:
        dbfilepath = Path(__file__).parent / "Students.db"
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_database):
            st.error("⚠️ Please fill in all MySQL credentials.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
))

# Establish Database Connection
try:
    if db_uri == LOCALDB:
        db = configure_db(db_uri)
    else:
        db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_database)
except Exception as e:
    st.error("❌ Error: Please check database credentials and try again.")
    st.stop()

# --- 🔧 Create Agent & Toolkit ---
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(llm, toolkit=toolkit, verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# --- 💬 Chat History ---
st.sidebar.subheader("💾 Chat History")
if "messages" not in st.session_state or st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

# Display chat messages with the new dark-themed UI
for msg in st.session_state.messages:
    role_class = "user-message" if msg["role"] == "user" else "assistant-message"
    st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# --- ⌨️ Chat Input ---
user_query = st.chat_input("🔎 Ask anything from your database...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.markdown(f'<div class="chat-message user-message">{user_query}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("⏳ Generating response..."):
            st_cb = StreamlitCallbackHandler(st.container())
            response = agent.run(user_query, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(f'<div class="chat-message assistant-message">{response}</div>', unsafe_allow_html=True)
