# Cold Mail Generator using LLM
A powerful cold email automation tool for B2B service companies, built using Groq, LangChain, Streamlit, and Vector Databases.
This tool enables business development teams to automatically extract job listings from any company's careers page and craft personalized cold emails, embedding relevant portfolio links that align with job descriptions.

# Real-world Use Case
Imagine Nike is hiring a Principal Software Engineer. Rather than going through long hiring cycles, Atliq, a software services company, wants to propose a dedicated engineer directly. Their business development executive, Mohan, uses this tool to send a cold email tailored to Nike’s job post — saving Nike both time and hiring costs.
This is outbound sales powered by AI.

This project leverages the power of Large Language Models to solve a real-world B2B problem — automating personalized cold outreach based on dynamic job listings.

# LLM Tasks handled:

Job description summarization

Contextual understanding of roles

Personalized email generation

Semantic search over portfolio content using vector embeddings

# LLM Platforms Used:
✅ Groq (for ultra-fast inference)
✅ LangChain (for prompt orchestration and modular LLM pipeline)

By combining web scraping, vector search, and LLMs, this project becomes a full-stack AI solution in the outbound sales domain — not just a chatbot or toy example, but a business-grade workflow.

# Tech Stack
# Component	           Purpose
Streamlit	           Web interface for input and email generation
LangChain	          LLM orchestration and workflow logic
Groq	              Fast LLM inference
BeautifulSoup	      Web scraping of career pages
FAISS / Chroma	    Vector DB to store and retrieve portfolio content
OpenAI or Groq      LLMs	Smart cold email generation

# Features
✅ Extracts job listings from careers pages
✅ Matches portfolio content from vector database
✅ Crafts highly-personalized cold emails
✅ Fast response generation using Groq LLMs
✅ Intuitive web UI with Streamlit

