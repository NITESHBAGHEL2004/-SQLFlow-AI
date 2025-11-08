import os
import streamlit as st
import pandas as pd
import mysql.connector
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import GoogleGenerativeAI
import random
import string

# ------------------------------------------------------------
# 🧠 Prompts
# ------------------------------------------------------------
SQL_QUERY_PROMPT = """
You are a MySQL assistant. Based on the schema, generate a valid SQL query.
If the user asks to "add random data", "insert data", or "generate sample rows",
create an INSERT query with realistic random values for all columns.

<SCHEMA>{schema}</SCHEMA>
Conversation History: {chat_history}

User Request: {question}
SQL Query:
"""

ERROR_EXPLANATION_PROMPT = """
You are a database expert. The following query failed. Explain briefly how to fix it.
SQL Query: {query}
Error: {error}
Explanation:
"""

# ------------------------------------------------------------
# 🔌 Database Functions
# ------------------------------------------------------------
def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(uri)


def run_dict_query(user: str, password: str, host: str, port: str, database: str, query: str):
    conn = mysql.connector.connect(
        host=host, user=user, password=password, port=port, database=database
    )
    with conn.cursor(dictionary=True) as cursor:
        try:
            cursor.execute(query)
            if query.strip().lower().startswith(("select", "show", "describe", "explain")):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = {"rows_affected": cursor.rowcount}
        except Exception as e:
            raise e
    conn.close()
    return result


# ------------------------------------------------------------
# 🧠 LangChain Chains
# ------------------------------------------------------------
def get_sql_chain(db: SQLDatabase, llm):
    prompt = ChatPromptTemplate.from_template(SQL_QUERY_PROMPT)
    return (
        RunnablePassthrough.assign(schema=lambda _: db.get_table_info())
        | prompt
        | llm
        | StrOutputParser()
    )


def explain_sql_error(sql_query: str, error: str, llm):
    prompt = ChatPromptTemplate.from_template(ERROR_EXPLANATION_PROMPT)
    return (
        RunnablePassthrough.assign(query=lambda _: sql_query, error=lambda _: error)
        | prompt
        | llm
        | StrOutputParser()
    ).invoke({
        "query": sql_query,
        "error": error
    })


# ------------------------------------------------------------
# ⚙️ Sidebar Configuration (API key input)
# ------------------------------------------------------------
def sidebar_config():
    st.sidebar.markdown("## ⚙️ Configuration")

    # Gemini API Key input (for free API)
    api_key = st.sidebar.text_input("🔑 Gemini API Key (AI Studio)", type="password", key="GeminiAPI")

    st.sidebar.text_input("Host", value="localhost", key="Host")
    st.sidebar.text_input("Port", value="3306", key="Port")
    st.sidebar.text_input("User", value="root", key="User")
    st.sidebar.text_input("Password", type="password", value="", key="Password")
    st.sidebar.text_input("Database", value="", key="Database")

    if st.sidebar.button("Connect"):
        try:
            with st.spinner("🔌 Connecting to MySQL..."):
                db = init_database(
                    st.session_state["User"],
                    st.session_state["Password"],
                    st.session_state["Host"],
                    st.session_state["Port"],
                    st.session_state["Database"]
                )
                st.session_state.db = db
                st.success("✅ Connected to database successfully!")
        except Exception as e:
            st.error(f"❌ Database connection failed: {str(e)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("🤖 **Built by Nitesh Singh**")
    return api_key


# ------------------------------------------------------------
# 💬 Chat UI + Logic (Simplified)
# ------------------------------------------------------------
def render_chat_messages():
    for message in st.session_state.chat_history:
        role = "ai" if isinstance(message, AIMessage) else "human"
        avatar = "🤖" if role == "ai" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message.content)


def handle_user_query(user_query: str, llm):
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("human", avatar="👤"):
        st.markdown(user_query)

    with st.chat_message("ai", avatar="🤖"):
        try:
            sql_chain = get_sql_chain(st.session_state.db, llm)
            sql_query = sql_chain.invoke({
                "chat_history": st.session_state.chat_history,
                "question": user_query
            }).strip()

            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

            # Run the SQL query
            result = run_dict_query(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"],
                sql_query
            )

            # Show generated SQL
            st.markdown("### 🧾 Generated SQL Query:")
            st.code(sql_query, language="sql")

            # Show result (table or message)
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                df = pd.DataFrame(result)
                st.markdown("### 📊 Query Result:")
                st.dataframe(df)
            else:
                st.success(f"✅ Query executed successfully. {result.get('rows_affected', 0)} rows affected.")

            # Save history
            st.session_state.chat_history.append(AIMessage(content=f"SQL Query: {sql_query}"))

        except Exception as e:
            error_message = explain_sql_error(user_query, str(e), llm)
            st.error("❌ Query failed.")
            st.markdown("### ❗ Error explanation:")
            st.markdown(error_message)
            st.session_state.chat_history.append(AIMessage(content=error_message))


# ------------------------------------------------------------
# 🚀 Run App
# ------------------------------------------------------------
st.set_page_config(page_title="SQLFlow – AI SQL Bot", page_icon="🤖")
st.title("🤖 SQLFlow – AI SQL Assistant")

api_key = sidebar_config()

# ✅ Use Gemini 2.0 Flash (Free-tier Model)
if api_key.strip():
    LLM = GoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
else:
    LLM = None
    st.warning("⚠️ Please enter your Gemini API Key (AI Studio) in the sidebar to continue.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="👋 Hello! I'm your AI SQL assistant. Ask me anything about your database.")
    ]

if "db" in st.session_state and LLM:
    render_chat_messages()
    user_input = st.chat_input("Ask anything about your database...")
    if user_input and user_input.strip():
        handle_user_query(user_input, LLM)
else:
    st.info("💡 Please connect to your database and enter your Gemini API Key to start chatting.")
