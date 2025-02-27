# Langchain: Chat with SQL

Langchain: Chat with SQL is an AI-powered application that allows users to interact with their databases using natural language. It supports both local SQLite and MySQL databases, making it easy to query and retrieve information seamlessly.

---

## 📌 Features

✅ Supports SQLite and MySQL databases  
✅ Natural language querying with LangChain & Groq  
✅ Streamlit-based interactive UI  
✅ Dark-themed chat interface  
✅ Chat history with clearing option  
✅ Secure environment variable management  
✅ Real-time query execution  

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/langchain-chat-sql.git
cd langchain-chat-sql
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file in the project root and add:
```env
LANGCHAIN_API_KEY=your_langchain_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## 🛠 Usage

### Run the Application
```bash
streamlit run app.py
```

### Database Configuration
- **SQLite**: Uses a local database file (`Students.db`).
- **MySQL**: Users must enter database credentials (host, user, password, database) in the Streamlit sidebar.

---

## 🏗️ Project Structure
```
📂 langchain-chat-sql
│── 📄 app.py               # Main Streamlit application
│── 📄 requirements.txt     # Dependencies
│── 📄 .env                 # Environment variables
│── 📄 Students.db          # Sample SQLite database
│── 📂 models/              # (Optional) Custom models or scripts
└── 📂 assets/              # UI assets (if needed)
```

---

## ⚡ How It Works
1. The user selects a database (SQLite or MySQL).
2. The application establishes a connection and initializes the SQL agent.
3. The user enters a query in natural language.
4. LangChain processes the query and retrieves relevant data.
5. The result is displayed in a chat-style UI with a dark theme.

---

## 🏆 Contribution
Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 🛡️ License
This project is licensed under the **Apache License 2.0**.

---

## 📬 Contact
For any queries, reach out via [your email or GitHub profile].

