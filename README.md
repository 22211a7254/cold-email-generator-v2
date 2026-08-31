# Cold Email Generator using LLM

An AI-powered cold email generation pipeline that uses **Groq, LangChain, ChromaDB, and Python** to analyze a job posting, identify relevant skills, retrieve matching portfolio links, and generate a personalized B2B cold email.

## 🎯 Project Goal

The goal of this project is to automate part of the business-development process. Instead of manually reading a job posting and finding relevant portfolio projects, the pipeline extracts important information from the job posting, searches a portfolio using semantic similarity, and uses an LLM to generate a personalized cold email.

## 🔄 How the Project Works

The current implementation follows a sequential pipeline:

```text
Job URL
   ↓
WebBaseLoader
   ↓
Job Page Text
   ↓
Groq LLM
   ↓
Structured Job Information
   ↓
ChromaDB Semantic Search
   ↓
Relevant Portfolio Links
   ↓
Groq LLM
   ↓
Personalized Cold Email
```

## 🧠 Main Components

### 1. Job Page Extraction

The project uses LangChain's `WebBaseLoader` to fetch the job page and convert the webpage into text.

The current notebook uses a job URL as a fixed input.

```python
loader = WebBaseLoader(job_url)
page_data = loader.load().pop().page_content
```

The resulting text is passed to the LLM for further processing.

### 2. Job Information Extraction

The scraped text is given to a Groq-hosted Llama model through LangChain.

The LLM is instructed to extract:

* Role
* Experience
* Skills
* Job description

The response is then parsed into Python data using `JsonOutputParser`.

Example structure:

```text
{
    "role": "Junior Data Scientist",
    "experience": "0 year(s)",
    "skills": [
        "Data Analytics",
        "Data Science",
        "Python",
        "SQL"
    ],
    "description": "..."
}
```

### 3. Portfolio Management

The project contains a portfolio CSV with technology stacks and corresponding links.

Example:

```text
Techstack                    Links
Python, Machine Learning     portfolio-link
React, Node.js               portfolio-link
TensorFlow, ML               portfolio-link
```

Pandas is used to load the portfolio data.

### 4. Semantic Portfolio Search

ChromaDB is used as the vector database.

Portfolio technology-stack information is stored as documents along with the corresponding links as metadata.

When job skills are extracted, they are used as queries against the ChromaDB collection to find semantically related portfolio information.

This helps connect the requirements of a job with relevant technical work from the portfolio.

### 5. Cold Email Generation

The extracted job information and retrieved portfolio links are passed to another LLM prompt.

The LLM is instructed to generate a cold email from the perspective of **Mohan, a Business Development Executive at AtliQ**.

The generated email contains:

* A suitable subject
* Greeting
* Understanding of the hiring requirement
* AtliQ's relevant capabilities
* Relevant portfolio links
* Professional closing

## 🛠️ Technology Stack

* **Python** – Core programming language
* **LangChain** – LLM orchestration and prompt pipelines
* **Groq** – LLM inference
* **Llama 3 70B** – Language model used in the original implementation
* **ChromaDB** – Vector database for portfolio retrieval
* **Pandas** – Portfolio data processing
* **Jupyter Notebook** – Development and experimentation environment

## 📂 Project Structure

```text
cold-email-generator/
│
├── cold Email generator (1).ipynb
├── main.py
├── chromadb.ipynb
├── Langchain.ipynb
├── resource/
│   └── my_portfolio.csv
├── README.md
└── requirements.txt
```

### Main Files

**`cold Email generator (1).ipynb`**

Contains the main end-to-end pipeline for job extraction, portfolio retrieval, and email generation.

**`main.py`**

Python export of the notebook cells.

**`resource/my_portfolio.csv`**

Contains portfolio technology stacks and associated links.

**`chromadb.ipynb`**

A separate experiment used to understand ChromaDB document storage, metadata, querying, and similarity search.

**`Langchain.ipynb`**

A separate experiment used to test the Groq LLM through LangChain.

## 🔑 LLM Pipeline

The project uses two main LLM calls.

### Call 1 — Job Extraction

```text
Scraped Job Page
       ↓
Prompt Template
       ↓
Groq LLM
       ↓
JSON Response
       ↓
JsonOutputParser
       ↓
Structured Job Data
```

### Call 2 — Email Generation

```text
Job Information
       +
Retrieved Portfolio Links
       ↓
Prompt Template
       ↓
Groq LLM
       ↓
Personalized Cold Email
```

The same LLM instance is reused for both tasks.

## 🔍 Vector Search

ChromaDB is used to perform semantic retrieval over portfolio technology stacks.

The basic process is:

```text
Portfolio Tech Stack
        ↓
Embedding
        ↓
Vector Database
        ↓
Job Skill Query
        ↓
Similarity Search
        ↓
Relevant Portfolio Results
```

The project uses ChromaDB's default embedding behavior rather than explicitly configuring an embedding model in the main generator code.

## ⚙️ Current Implementation

The current version is primarily a **linear LLM pipeline**, rather than a fully autonomous AI agent.

The execution follows a predefined sequence:

```text
Scrape → Extract → Parse → Retrieve → Generate
```

There is no autonomous tool selection or agent-based decision loop in the current implementation.

## ⚠️ Current Limitations

This project is currently a prototype and has several areas that can be improved:

* Job URL is currently provided directly in the notebook.
* There is no dedicated web UI in the current implementation.
* Job-page scraping can depend on the structure and accessibility of the website.
* LLM-generated JSON requires reliable validation.
* Portfolio retrieval can be improved with better query construction and retrieval evaluation.
* The vector database should be managed carefully to avoid stale or unrelated records.
* There is no automated evaluation of email quality or retrieval relevance.
* The generated email is currently printed as output rather than automatically sent.

## 🚀 Future Improvements

Possible improvements include:

* Add a Streamlit interface for entering job URLs.
* Support multiple job postings.
* Improve structured LLM output validation.
* Use hybrid keyword + vector search.
* Add retrieval evaluation and ranking.
* Add email quality evaluation.
* Add retry and error-handling mechanisms.
* Integrate an email service for sending approved emails.
* Explore agent-based architecture where dynamic tool selection is actually useful.
* Add monitoring and observability for LLM calls and retrieval quality.

## 📚 What I Learned

Through this project, I practiced:

* Working with LLM APIs
* LangChain prompt pipelines
* Structured output parsing
* Web-page text extraction
* Vector databases
* Semantic search
* Portfolio-to-job matching
* Prompt engineering
* Building an end-to-end AI workflow

The project also helped me understand an important distinction between a **fixed LLM pipeline and an autonomous AI agent**, and the importance of evaluating retrieval quality rather than assuming that semantic search always produces relevant results.

## 👨‍💻 Project Learning Focus

The next stage of this project is focused on understanding and evaluating the existing architecture rather than simply adding more features. In particular, the areas of interest are:

* RAG and retrieval quality
* LLM evaluation
* Structured outputs
* Agent architectures
* Tool calling
* Modern AI development workflows
