
import os
import re
import json
import uuid
import pandas as pd
import chromadb

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY missing. Add it to your .env file."
    )

JOB_URL = (
    "https://internshala.com/job/detail/fresher-remote-junior-data-scientist-job-at-mediacom-india1753532936"
)

PORTFOLIO_PATH = "resource/my_portfolio.csv"

os.environ.setdefault(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
)

# --------------------------------------------------
# 2. CONNECT TO GROQ
# --------------------------------------------------

llm = ChatGroq(
    temperature=0,
    groq_api_key='add api key',
    model_name="openai/gpt-oss-120b"
)

print("\nGroq connection successful!")

# --------------------------------------------------
# 3. LOAD JOB DESCRIPTION FROM WEBSITE
# --------------------------------------------------

print("\nReading job description...")

try:
    loader = WebBaseLoader(
        web_path=JOB_URL,
        requests_kwargs={
            "headers": {
                "User-Agent": os.environ["USER_AGENT"]
            },
            "timeout": 30
        }
    )

    documents = loader.load()

    if not documents:
        raise ValueError("The website returned no content.")

    page_data = documents[0].page_content.strip()

    if len(page_data) < 300:
        raise ValueError("The job page contains insufficient text.")

    blocked_phrases = [
        "access denied",
        "403 forbidden",
        "page not found",
        "captcha",
        "enable javascript"
    ]

    if any(
        phrase in page_data.lower()
        for phrase in blocked_phrases
    ):
        raise ValueError("The website blocked automated access.")

    print("Job page loaded successfully!")

except Exception as e:
    raise RuntimeError(
        f"Could not read the job page: {e}\n"
        "Try another public job URL or provide the job "
        "description text directly."
    )

# --------------------------------------------------
# 4. EXTRACT JOB DETAILS
# --------------------------------------------------

prompt_extract = PromptTemplate.from_template("""
You are a job description extraction assistant.

Extract the information from the job page below.

JOB PAGE:
{page_data}

Return ONLY a valid JSON object with these keys:

{{
    "role": "Job title",
    "experience": "Required experience",
    "skills": ["skill 1", "skill 2"],
    "description": "Short job description"
}}

Rules:
- Do not invent missing information.
- If a field is unavailable, use an empty string or empty list.
- Do not include Markdown or explanations.
""")

print("\nExtracting job information...")

extract_chain = prompt_extract | llm

response = extract_chain.invoke({
    "page_data": page_data[:18000]
})

# Remove Markdown code fences if the model adds them
raw_json = response.content.strip()
raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
raw_json = re.sub(r"\s*```$", "", raw_json)

try:
    job = json.loads(raw_json)

    if isinstance(job, list):
        if not job:
            raise ValueError("No job records returned.")
        job = job[0]

except (json.JSONDecodeError, ValueError, TypeError) as e:
    raise ValueError(
        f"Could not parse job details as JSON.\n"
        f"Model response: {raw_json}"
    ) from e

if not isinstance(job, dict):
    raise ValueError("The extracted job details are not a JSON object.")

if not job.get("role") or not job.get("skills"):
    raise ValueError(
        "Job title or skills are missing. "
        "The website may not contain a readable job description."
    )

print("\nEXTRACTED JOB DETAILS")
print(json.dumps(job, indent=4, ensure_ascii=False))

# --------------------------------------------------
# 5. LOAD PORTFOLIO CSV
# --------------------------------------------------

print("\nLoading portfolio...")

if not os.path.exists(PORTFOLIO_PATH):
    raise FileNotFoundError(
        f"Portfolio CSV not found: {PORTFOLIO_PATH}"
    )

df = pd.read_csv(PORTFOLIO_PATH)

required_columns = {"Techstack", "Links"}

if not required_columns.issubset(df.columns):
    raise ValueError(
        "CSV must contain these columns: Techstack and Links."
    )

df = df.dropna(subset=["Techstack", "Links"])

if df.empty:
    raise ValueError("No valid portfolio records found in CSV.")

# --------------------------------------------------
# 6. CREATE CHROMADB VECTOR DATABASE
# --------------------------------------------------

print("\nCreating portfolio vector database...")

client = chromadb.PersistentClient(path="vectorstore")

# Rebuild collection so old portfolio records are not reused
try:
    client.delete_collection(name="portfolio")
except Exception:
    pass

collection = client.create_collection(name="portfolio")

for _, row in df.iterrows():
    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[str(row["Techstack"])],
        metadatas=[{"links": str(row["Links"])}]
    )

print("Portfolio database created!")

# --------------------------------------------------
# 7. SEARCH RELEVANT PORTFOLIO LINKS
# --------------------------------------------------

print("\nSearching relevant portfolio projects...")

skills = job["skills"]

if isinstance(skills, list):
    search_query = ", ".join(str(skill) for skill in skills)
else:
    search_query = str(skills)

results = collection.query(
    query_texts=[search_query],
    n_results=min(3, collection.count())
)

links = results.get("metadatas", [[]])[0]

if not links:
    raise ValueError("No relevant portfolio links were found.")

print("\nRELEVANT PORTFOLIO LINKS:")
for item in links:
    print(item["links"])

# --------------------------------------------------
# 8. GENERATE PERSONALIZED COLD EMAIL
# --------------------------------------------------

print("\nGenerating cold email...")

prompt_email = PromptTemplate.from_template("""
You are Mohan, a Business Development Executive at AtliQ,
an AI and Software Consulting company.

Write a professional and personalized cold email based
on the actual job description below.

JOB DETAILS:
{job_description}

RELEVANT PORTFOLIO LINKS:
{link_list}

Instructions:
1. Write a suitable subject line.
2. Address the hiring team professionally.
3. Explain how AtliQ's services match the actual job requirements.
4. Include only the relevant portfolio links provided.
5. Keep the email concise and professional.
6. Do not invent achievements, clients, phone numbers,
   email addresses, or company website details.
7. Do not invent job requirements.
8. Return only the email. No preamble.
""")

email_chain = prompt_email | llm

email_response = email_chain.invoke({
    "job_description": json.dumps(job, ensure_ascii=False),
    "link_list": json.dumps(links, ensure_ascii=False)
})

# --------------------------------------------------
# 9. DISPLAY FINAL EMAIL
# --------------------------------------------------

print("\n" + "=" * 60)
print("GENERATED COLD EMAIL")
print("=" * 60)

print(email_response.content)

print("\n" + "=" * 60)
print("PROJECT EXECUTION COMPLETED SUCCESSFULLY!")
print("=" * 60)
