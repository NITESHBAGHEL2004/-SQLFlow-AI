SQLFlow AI — LangChain + Gemini-Powered MySQL Assistant

SQLFlow AI is an intelligent SQL assistant built with Streamlit, LangChain, and Google Gemini AI (Free API from Google AI Studio).
It allows users to chat in natural language and automatically generate, execute, and visualize SQL queries for a connected MySQL database — all without writing a single line of SQL.

🚀 Features

✅ AI-Powered SQL Generation
Type queries in plain English (e.g., “Show all employees with salary above 50000”) and get the exact SQL instantly.

✅ Automatic Execution
The generated SQL query runs automatically on your connected MySQL database.

✅ Real-Time Results
Results are displayed as a clean, interactive table or a success message (for non-select operations).

✅ Gemini AI Integration (Free API)
Uses Google’s Gemini 2.0 Flash model — fast, accurate, and available on the free tier via Google AI Studio
.

✅ No Hardcoded API Keys
You can safely enter your Gemini API key from the sidebar — no .env file needed.

✅ Error Explanation
If a query fails, the AI provides a simple explanation and how to fix it.

✅ Simple UI
Powered by Streamlit with a clean chat-like interface.

🏗️ Tech Stack
Component	Technology Used
Frontend	Streamlit (Chat UI)
AI Engine	LangChain + Google Gemini
Database	MySQL
Language	Python
Model	gemini-2.0-flash (Free-tier model)
⚙️ Installation
1️⃣ Clone this Repository
git clone https://github.com/yourusername/sqlflow-ai.git
cd sqlflow-ai

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

3️⃣ Install Dependencies
pip install -r requirements.txt


Example requirements.txt

streamlit
mysql-connector-python
pandas
langchain
langchain-core
langchain-community
langchain-google-genai

🔑 Get a Free Gemini API Key

Go to Google AI Studio

Click “Create API Key”

Copy your API key — it looks like this:

AIzaSyD2s52ehK-udDMLxAcodvliMaqqTYLsZeY

🧠 Run the App
streamlit run index.py


Then open the provided local URL (e.g., http://localhost:8501) in your browser.

🧰 Usage Guide

Enter Your API Key

In the sidebar, paste your Gemini API key.

Connect to MySQL

Enter your MySQL credentials (Host, Port, User, Password, Database).

Click “Connect”.

Start Asking!

Example prompts:

“Show all tables.”

“Create a table named employees with id, name, and salary.”

“Insert random data into employees.”

“Show employees with salary > 50000.”

“Update salary where id = 2.”

“Delete records where salary < 40000.”

View Results Instantly

The generated SQL and result table are shown together.

No natural language explanation (cleaner UI).