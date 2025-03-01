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

# --- Custom CSS for Dark Chat Styling ---
st.markdown("""
    <style>
        .chat-message {
            padding: 12px;
            border-radius: 8px;
            margin: 5px 0;
            color: white;
            font-weight: 500;
        }
        .user-message {
            background-color: #003366;
            text-align: right;
        }
        .assistant-message {
            background-color: #FF7F50;
            text-align: left;
        }
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            color: white;
        }
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

# MySQL Configuration Inputs
mysql_host = None
mysql_user = None
mysql_password = None
mysql_database = None
db = None

if selected_db == "Select MySQL Database":
    db_uri = MYSQL
    with st.sidebar.expander("🔧 MySQL Configuration"):
        mysql_host = st.text_input("MySQL Host", placeholder="e.g., localhost")
        mysql_user = st.text_input("MySQL User", placeholder="e.g., root")
        mysql_password = st.text_input("MySQL Password", type="password")
        mysql_database = st.text_input("MySQL Database", placeholder="e.g., test_db")

    # Add a "Connect" button
    if st.sidebar.button("🔗 Connect to MySQL"):
        if not all([mysql_host, mysql_user, mysql_password, mysql_database]):
            st.sidebar.error("⚠️ Please fill in all MySQL credentials.")
        else:
            try:
                db = SQLDatabase(
                    create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}")
                )
                st.sidebar.success(f"✅ Connected to `{mysql_database}` successfully!")
            except Exception as e:
                st.sidebar.error(f"❌ Connection failed: {e}")

else:
    db_uri = LOCALDB
    dbfilepath = Path(__file__).parent / "Students.db"
    creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
    db = SQLDatabase(create_engine("sqlite:///", creator=creator))

# Error Handling
if not db:
    st.error("⚠️ No database connection established. Please select a database and connect.")
    st.stop()

# --- 🤖 Initialize LLM ---
llm = ChatGroq(groq_api_key=groq_api, model_name="Llama-3.3-70b-Versatile", streaming=True)

# --- 🔧 Create Agent & Toolkit ---
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(llm, toolkit=toolkit, verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# --- 💬 Chat History ---
st.sidebar.subheader("💾 Chat History")
if "messages" not in st.session_state or st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

# Display chat messages
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
