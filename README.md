# AI Career Assistant (RAG Platform)

An AI-powered Careers Assistant that provides candidates with instant, accurate answers about roles, benefits, interview processes, and company policies. Built with a robust Retrieval-Augmented Generation (RAG) architecture, this platform guarantees high accuracy and strictly eliminates LLM hallucinations by enforcing local context grounding.

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)

## 🔗 Live Links

- **Frontend (Vercel):** [https://ai-chatbot-application-status.vercel.app/](https://ai-chatbot-application-status.vercel.app/)
- **Backend API (Render):** [https://ai-chatbot-application-status.onrender.com](https://ai-chatbot-application-status.onrender.com)

## Features

- **Hybrid Vector Search:** Combines FAISS (FastEmbed) vector similarity and BM25 keyword matching with Reciprocal Rank Fusion (RRF) for lightning-fast, highly relevant retrieval.
- **Strict Anti-Hallucination:** Refuses to answer queries that fall outside of the uploaded knowledge base.
- **Dynamic Knowledge Base:** Drag-and-drop PDF ingestion to easily update the bot's memory context.
- **Recruiter Dashboard:** An admin panel that tracks conversation logs, flags unanswered queries, and captures candidate leads.

##  How to Use

1. **Open the live application:** Visit the [Frontend URL](https://ai-chatbot-application-status.vercel.app/). *(No login required)*
2. **Upload Context:** Upload your company policy PDFs or job descriptions (if prompted by the interface).
3. **Ask Questions:** Chat with the assistant. Try asking:
   - *"What’s the salary for Backend Engineer?"*
   - *"What are the Benefits & Perks at Vertex Labs?"*
   - *"What’s the salary range for Product Manager?"*
   - *"Describe the Vertex Labs Interview Process."*
4. **Submit Interest:** If you find a role you like, click the **Interested** button to submit your email and preferred role to the recruiter.
5. **Admin Analytics:** Visit `/admin` to view real-time conversation logs, success rates, and the most frequently asked questions.

## Local Development

### 1. Backend Setup
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# Create a .env file and add your Gemini API Key
# GEMINI_API_KEY=your_key_here

# Run the Flask API
python app.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install

# Run the Vite development server
npm run dev
```

---
*Developed for instant, intelligent candidate engagement.*
