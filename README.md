# 🚀 AI Cold Email Generator | Generative AI & LLM Application

An AI-powered application that analyzes job descriptions, identifies relevant skills, retrieves matching portfolio projects using semantic search, and generates personalized professional cold emails.

Built using **Python, Generative AI, LangChain, Groq GPT-OSS-120B, ChromaDB, and Streamlit**.

## 📌 Project Overview

The AI Cold Email Generator automates the process of creating personalized professional cold emails based on job requirements and relevant portfolio information.

Users can enter a job posting URL or manually paste a job description. The application analyzes the content using a Large Language Model (LLM), extracts structured job information, searches for matching portfolio projects, and generates a professional cold email.

The project demonstrates how LLMs, prompt engineering, vector databases, and semantic search can be integrated into an end-to-end Generative AI application.

## 🎯 Project Objectives

- Automate job description analysis.
- Extract important job requirements using an LLM.
- Match job skills with relevant portfolio projects.
- Retrieve portfolio links using semantic search.
- Generate personalized professional cold emails.
- Provide an interactive interface for reviewing, editing, and downloading emails.

## 🔄 Application Workflow

```text
       Job Posting URL
              |
              v
     Web Page Extraction
       (Requests / BS4)
              |
              v
      Job Description Text
              |
              v
       LangChain Pipeline
              |
              v
       Groq GPT-OSS-120B
              |
              v
     Structured Job Details
       (Role, Skills, etc.)
              |
              v
       Portfolio CSV Data
              |
              v
        ChromaDB Search
              |
              v
     Relevant Portfolio Links
              |
              v
       LangChain Prompt
              |
              v
       Groq GPT-OSS-120B
              |
              v
    Personalized Cold Email
              |
              v
       Streamlit Interface
              |
              v
       Review / Edit / Download
```

## ⚙️ Key Features

### 1. Job Description Extraction

- Accepts job posting URLs.
- Extracts webpage content using Python, Requests, and BeautifulSoup.
- Supports manually pasting job descriptions when automatic extraction is unavailable.

### 2. LLM-Based Job Analysis

Integrates LangChain with Groq's GPT-OSS-120B model to analyze job descriptions and identify:

- Job role
- Required experience
- Technical skills
- Job description and requirements

Structured output is used for the next stages of the pipeline.

### 3. Portfolio Management

Uses a CSV file to maintain portfolio information, including:

- Project technology stacks
- Relevant project links

Pandas is used to load and process portfolio information.

### 4. Semantic Portfolio Search

ChromaDB is integrated as the vector database.

The application uses semantic search to retrieve portfolio projects relevant to the skills extracted from the job description.

This helps connect job requirements with suitable portfolio examples.

### 5. Personalized Cold Email Generation

The application passes extracted job details and retrieved portfolio links to the Groq LLM.

The generated email includes:

- Subject line
- Professional greeting
- Understanding of the hiring requirements
- Relevant capabilities
- Matching portfolio links
- Professional closing

The current prompt generates B2B business outreach emails from the perspective of Mohan, Business Development Executive at AtliQ.

### 6. Interactive Streamlit Interface

- Simple and user-friendly interface.
- Job URL and manual description input.
- Job information and portfolio matching.
- Generated email preview.
- Email editing functionality.
- Download generated email as a text file.

## 🧠 LLM Architecture

The application uses two primary LLM operations.

**Call 1: Job Information Extraction**

```text
Job Description
      |
      v
LangChain Prompt
      |
      v
Groq GPT-OSS-120B
      |
      v
Structured Job Information
```

**Call 2: Cold Email Generation**

```text
Extracted Job Details
          +
Retrieved Portfolio Links
          |
          v
    LangChain Prompt
          |
          v
  Groq GPT-OSS-120B
          |
          v
 Personalized Cold Email
```

The same configured LLM model is used for both operations.

## 🔍 Retrieval and Semantic Search

The portfolio retrieval workflow follows these stages:

```text
Portfolio CSV
      |
      v
Technology Stack Data
      |
      v
ChromaDB Collection
      |
      v
Semantic Similarity Search
      |
      v
Relevant Portfolio Results
      |
      v
LLM Context for Email Generation
```

The retrieved portfolio information is incorporated into the email-generation prompt. This represents a simple retrieval-augmented, RAG-style workflow.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Generative AI | Groq GPT-OSS-120B |
| LLM Framework | LangChain |
| Vector Database | ChromaDB |
| Frontend | Streamlit |
| Data Processing | Pandas |
| Web Extraction | Requests, BeautifulSoup |
| Development | VS Code, Jupyter Notebook |
| Version Control | Git, GitHub |

## 📂 Project Structure

```text
cold-email-generator-v2/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
│
├── resource/
│   └── my_portfolio.csv
│
├── chromadb.ipynb
├── Langchain.ipynb
├── cold Email generator (1).ipynb
│
├── .gitignore
└── .env                 # Local environment file; not committed
```

Note: `vectorstore/` may be created locally when the application runs. It is excluded from Git if configured in `.gitignore`.

## 🚀 Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Groq API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/22211a7254/cold-email-generator-v2.git
cd cold-email-generator-v2
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory.

Add your own Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Never upload your API key to GitHub.

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

## 🔐 Environment and Security

- API credentials are loaded from environment variables.
- The `.env` file must remain local.
- Virtual environments and generated database files should not be committed.
- Never expose API keys in source code, notebooks, screenshots, or public repositories.

## ⚠️ Current Limitations

- Job-page extraction depends on website accessibility and page structure.
- Some websites may block automated scraping.
- LLM-generated output may require manual review.
- Portfolio matching depends on the quality of the available project descriptions and technology-stack data.
- Retrieval relevance and email quality are not yet evaluated through a formal automated testing framework.
- The application generates email drafts; it does not automatically send emails.
- The project is a sequential LLM pipeline, not a fully autonomous AI agent.

## 🚀 Future Enhancements

- Support multiple job postings and job platforms.
- Improve structured output validation and error handling.
- Experiment with hybrid keyword and vector search.
- Evaluate portfolio retrieval relevance.
- Introduce automated email-quality evaluation.
- Add logging, monitoring, and LLM usage tracking.
- Explore agent-based workflows and tool calling.
- Integrate an email service for sending user-approved messages.

## 📚 Key Concepts and Learning Outcomes

Through this project, I gained practical experience with:

- Large Language Model integration.
- Generative AI application development.
- LangChain prompt engineering and orchestration.
- Structured information extraction.
- Web scraping and text processing.
- Vector databases and semantic search.
- Retrieval-augmented generation concepts.
- Building interactive applications using Streamlit.
- Integrating multiple AI components into an end-to-end workflow.

I also explored the difference between a fixed LLM pipeline and an autonomous AI agent, understanding when each architecture is appropriate.

## 👩‍💻 Author

**Samala Laxmi Prasanna**

B.Tech – Artificial Intelligence and Data Science

**Areas of Interest:** Artificial Intelligence, Machine Learning, Generative AI, LLM Applications, and Data Science.

**GitHub:** https://github.com/22211a7254

---
