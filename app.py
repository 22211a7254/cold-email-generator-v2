
import os
import re
import json
import requests
import pandas as pd
import streamlit as st

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import chromadb


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="AI Cold Email Generator",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_NAME = "openai/gpt-oss-120b"
PORTFOLIO_PATH = "resource/my_portfolio.csv"
CHROMA_PATH = "vectorstore"
COLLECTION_NAME = "portfolio"

# Read API key securely from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# 2. CUSTOM CSS - PROFESSIONAL UI
# ============================================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(
        135deg,
        #F8FAFF 0%,
        #EEF2FF 55%,
        #F5F3FF 100%
    );
}

/* Main content */
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1 {
    color: #312E81 !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #3730A3 !important;
    font-weight: 700 !important;
}

/* Normal text */
p, label, .stMarkdown {
    color: #334155;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #172554,
        #312E81,
        #4C1D95
    );
}

/* Sidebar technology names in white */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
    color: #FFFFFF !important;
}

/* Sidebar bullet points */
section[data-testid="stSidebar"] ul {
    color: #FFFFFF !important;

}

/* Input fields */
.stTextInput input,
.stTextArea textarea {
    border: 1.5px solid #C7D2FE !important;
    border-radius: 12px !important;
    background-color: white !important;
    color: #1E293B !important;
}

/* Focus effect */
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 2px #DDD6FE !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #4F46E5, #7C3AED);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.2rem;
    font-weight: 700;
    transition: all 0.2s ease;
}

/* Button hover */
.stButton > button:hover {
    background: linear-gradient(90deg, #3730A3, #6D28D9);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(79, 70, 229, 0.25);
}

/* Download button */
.stDownloadButton > button {
    background: #0F766E;
    color: white !important;
    border-radius: 10px;
    border: none;
    font-weight: 700;
}

/* Cards */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DDD6FE;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 12px rgba(49, 46, 129, 0.05);
}

/* Expanders */
div[data-testid="stExpander"] {
    background: white;
    border: 1px solid #DDD6FE;
    border-radius: 12px;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Divider */
hr {
    border-color: #DDD6FE;
}

/* Header */
header[data-testid="stHeader"] {
    background: transparent;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. SESSION STATE
# ============================================================

if "job_details" not in st.session_state:
    st.session_state.job_details = None

if "portfolio_links" not in st.session_state:
    st.session_state.portfolio_links = []

if "generated_email" not in st.session_state:
    st.session_state.generated_email = ""

if "job_description" not in st.session_state:
    st.session_state.job_description = ""


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def get_llm():
    """Create the Groq language model."""

    if not GROQ_API_KEY:
        raise ValueError(
            "Groq API key not found. Add GROQ_API_KEY to your .env file."
        )

    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.3,
        groq_api_key=GROQ_API_KEY
    )


def load_job_description(url, manual_text):
    """
    Get job description either from pasted text
    or by extracting text from a job posting URL.
    """

    if manual_text and manual_text.strip():
        return manual_text.strip()

    if not url or not url.strip():
        raise ValueError(
            "Please enter a job URL or paste the job description."
        )

    if not url.startswith(("http://", "https://")):
        raise ValueError("Please enter a valid URL starting with http:// or https://.")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=25
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unnecessary HTML elements
    for element in soup([
        "script", "style", "nav", "footer",
        "header", "noscript", "svg"
    ]):
        element.decompose()

    page_text = soup.get_text(separator="\n", strip=True)

    if len(page_text) < 300:
        raise ValueError(
            "The website did not provide enough readable text. "
            "Please paste the job description manually."
        )

    return page_text[:18000]


def extract_json(text):
    """Extract JSON from an LLM response."""

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return json.loads(match.group())

    raise ValueError("Could not read structured job details from the AI response.")


# ============================================================
# 5. EXTRACT JOB DETAILS
# ============================================================

def extract_job_details(job_description):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
You are an expert job description analyzer.

Analyze the following job description and return ONLY valid JSON.

Extract:
- role: Job title
- experience: Required experience
- skills: List of important technical skills
- description: Short summary of the role
- location: Job location
- job_type: Full-time, internship, remote, etc.

Do not invent missing information.
If a field is unavailable, return "Not specified".
If skills are unavailable, return an empty list.

JOB DESCRIPTION:
{job_description}

Return JSON in this exact structure:

{{
    "role": "",
    "experience": "",
    "skills": [],
    "description": "",
    "location": "",
    "job_type": ""
}}
""")

    chain = prompt | llm

    response = chain.invoke({
        "job_description": job_description
    })

    result = extract_json(response.content)

    if not isinstance(result, dict) or not result.get("role"):
        raise ValueError("The AI could not identify the job title. Try another description.")

    if not isinstance(result.get("skills"), list):
        result["skills"] = []

    return result


# ============================================================
# 6. PORTFOLIO MATCHING USING CHROMADB
# ============================================================

def get_portfolio_matches(skills):

    if not os.path.exists(PORTFOLIO_PATH):
        raise FileNotFoundError(
            f"Portfolio file not found: {PORTFOLIO_PATH}"
        )

    df = pd.read_csv(PORTFOLIO_PATH)

    required_columns = {"Techstack", "Links"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Your portfolio CSV must contain Techstack and Links columns."
        )

    df = df.dropna(subset=["Techstack", "Links"])

    if df.empty:
        return []

    df["Techstack"] = df["Techstack"].astype(str)
    df["Links"] = df["Links"].astype(str)

    # Create ChromaDB persistent client
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Update the collection with the latest CSV records
    existing = collection.get()

    if existing.get("ids"):
        collection.delete(ids=existing["ids"])

    ids = [f"project_{i}" for i in range(len(df))]

    documents = df["Techstack"].tolist()

    metadatas = [
        {"link": link, "techstack": tech}
        for link, tech in zip(df["Links"], df["Techstack"])
    ]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    if not skills:
        return []

    query_text = ", ".join(str(skill) for skill in skills)

    results = collection.query(
        query_texts=[query_text],
        n_results=min(3, len(df))
    )

    matches = []

    result_metadatas = results.get("metadatas", [[]])[0]

    for item in result_metadatas:
        matches.append({
            "techstack": item["techstack"],
            "link": item["link"]
        })

    return matches


# ============================================================
# 7. GENERATE COLD EMAIL
# ============================================================

def generate_email(job_details, portfolio_links):

    llm = get_llm()

    portfolio_text = "\n".join(
        [
            f"Technology: {item['techstack']}\n"
            f"Portfolio link: {item['link']}"
            for item in portfolio_links
        ]
    )

    if not portfolio_text:
        portfolio_text = "No matching portfolio links available."

    prompt = ChatPromptTemplate.from_template("""
You are Mohan, a Business Development Executive at AtliQ.

AtliQ provides technology and data-related services.

Your task is to write a professional, personalized cold email
to a company that is hiring for a new role.

The email should:
1. Mention the hiring role.
2. Explain how AtliQ's services could support the company's needs.
3. Connect relevant technologies to the job requirements.
4. Include relevant portfolio links when available.
5. Have a clear and polite call to action.
6. Be professional, concise and natural.
7. Avoid making unsupported claims.
8. Include a suitable subject line.

JOB DETAILS:
{job_details}

RELEVANT PORTFOLIO:
{portfolio}

Write only the email.
""")

    chain = prompt | llm

    response = chain.invoke({
        "job_details": json.dumps(job_details, indent=2),
        "portfolio": portfolio_text
    })

    return response.content.strip()


# ============================================================
# 8. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 📧 Cold Email AI")

    st.markdown("---")

    st.markdown("### 🚀 About this project")

    st.write(
        "An AI-powered application that analyzes job postings, "
        "finds relevant portfolio projects, and generates "
        "personalized professional cold emails."
    )

    st.markdown("---")

    st.markdown("### 🧠 Technologies")

    st.markdown("""
    - Python
    - LangChain
    - Groq LLM
    - ChromaDB
    - Streamlit
    - BeautifulSoup
    """)

    st.markdown("---")

    st.markdown("### ⚙️ Application status")

    if GROQ_API_KEY:
        st.success("Groq API key configured")
    else:
        st.error("Groq API key missing")

    if os.path.exists(PORTFOLIO_PATH):
        st.success("Portfolio file found")
    else:
        st.warning("Portfolio file missing")

    st.markdown("---")

    if st.button("🔄 Reset Application", use_container_width=True):

        st.session_state.job_details = None
        st.session_state.portfolio_links = []
        st.session_state.generated_email = ""
        st.session_state.job_description = ""

        st.rerun()

    st.caption("Built with Python and Generative AI")


# ============================================================
# 9. MAIN HEADER
# ============================================================

st.markdown("""
# 📧 AI Cold Email Generator

### Turn job descriptions into personalized professional outreach.

Generate relevant emails using **LangChain + Groq + ChromaDB**.
""")

st.markdown("---")


# ============================================================
# 10. DASHBOARD METRICS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="AI Model",
        value="Groq LLM",
        delta="Connected" if GROQ_API_KEY else "API key needed"
    )

with col2:
    st.metric(
        label="Portfolio Engine",
        value="ChromaDB",
        delta="Semantic Search"
    )

with col3:
    st.metric(
        label="Application",
        value="Streamlit",
        delta="Ready to use"
    )

st.markdown("---")


# ============================================================
# 11. JOB INPUT SECTION
# ============================================================

st.markdown("## 1. 🔍 Enter Job Details")

left_col, right_col = st.columns(2)

with left_col:

    st.markdown("### 🔗 Job Posting URL")

    job_url = st.text_input(
        "Paste job URL",
        placeholder="https://company.com/careers/job-details",
        help="Paste the job posting URL here."
    )

with right_col:

    st.markdown("### 📝 Job Description")

    manual_description = st.text_area(
        "Or paste the job description",
        height=140,
        placeholder="Paste the complete job description here..."
    )

st.info(
    "💡 If the job website blocks automated access, "
    "paste the complete job description manually."
)

st.markdown("")


# ============================================================
# 12. GENERATE BUTTON
# ============================================================

generate_button = st.button(
    "✨ Generate Personalized Cold Email",
    use_container_width=True,
    type="primary"
)


if generate_button:

    if not GROQ_API_KEY:

        st.error(
            "Groq API key is missing. Add a valid key to your .env file."
        )

    elif not job_url.strip() and not manual_description.strip():

        st.warning(
            "Please enter a job URL or paste a job description."
        )

    else:

        try:

            # Step 1: Load job description
            with st.status(
                "Analyzing the job posting...",
                expanded=True
            ) as status:

                st.write("🌐 Reading job description...")

                job_text = load_job_description(
                    job_url,
                    manual_description
                )

                st.session_state.job_description = job_text

                st.write("🤖 Extracting job requirements using Groq...")

                job_details = extract_job_details(job_text)

                st.session_state.job_details = job_details

                st.write("🔎 Finding relevant portfolio projects...")

                portfolio_links = get_portfolio_matches(
                    job_details.get("skills", [])
                )

                st.session_state.portfolio_links = portfolio_links

                st.write("✉️ Generating personalized email...")

                email = generate_email(
                    job_details,
                    portfolio_links
                )

                st.session_state.generated_email = email

                status.update(
                    label="Cold email generated successfully!",
                    state="complete",
                    expanded=False
                )

            st.success("Your personalized cold email is ready!")

        except Exception as e:

            st.error(f"Something went wrong: {str(e)}")

            st.info(
                "If URL extraction failed, paste the complete job "
                "description manually and try again."
            )


# ============================================================
# 13. RESULTS DASHBOARD
# ============================================================

if st.session_state.job_details:

    st.markdown("---")

    st.markdown("## 2. 📊 Extracted Job Information")

    details = st.session_state.job_details

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 💼 Role")

        st.markdown(f"**{details.get('role', 'Not specified')}**")

        st.markdown("### 📍 Location")

        st.write(details.get("location", "Not specified"))

        st.markdown("### ⏳ Experience")

        st.write(details.get("experience", "Not specified"))

    with col2:

        st.markdown("### 🏢 Job Type")

        st.write(details.get("job_type", "Not specified"))

        st.markdown("### 🛠️ Required Skills")

        skills = details.get("skills", [])

        if skills:
            st.write("  •  ".join(str(skill) for skill in skills))
        else:
            st.write("No specific skills extracted.")

    st.markdown("### 📄 Job Summary")

    st.info(details.get("description", "No summary available."))


    # --------------------------------------------------------
    # PORTFOLIO RESULTS
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown("## 3. 🔎 Relevant Portfolio Projects")

    portfolio_links = st.session_state.portfolio_links

    if portfolio_links:

        st.write(
            "ChromaDB found these portfolio entries based on "
            "the required job skills."
        )

        for index, item in enumerate(portfolio_links, start=1):

            with st.container(border=True):

                st.markdown(f"**Project Match {index}**")

                st.write(f"🛠️ Technologies: {item['techstack']}")

                st.markdown(f"🔗 [View Portfolio]({item['link']})")

    else:

        st.warning(
            "No matching portfolio projects were found. "
            "Check your portfolio CSV file."
        )


    # --------------------------------------------------------
    # GENERATED EMAIL
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown("## 4. ✉️ Generated Cold Email")

    st.write(
        "Review and edit the email before using it."
    )

    edited_email = st.text_area(
        "Your generated email",
        value=st.session_state.generated_email,
        height=350,
        key="email_editor"
    )

    st.session_state.generated_email = edited_email

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            label="⬇️ Download Email",
            data=edited_email,
            file_name="personalized_cold_email.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col2:

        st.button(
            "🔄 Generate Again",
            on_click=lambda: st.session_state.update({
                "generated_email": ""
            }),
            use_container_width=True
        )

    st.caption(
        "Always verify the recipient, company details, portfolio links, "
        "and email content before sending."
    )


# ============================================================
# 14. FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:20px; color:#64748B;">
        <h4 style="color:#4338CA;">📧 AI Cold Email Generator</h4>
        <p>Built using Python | LangChain | Groq | ChromaDB | Streamlit</p>
        <small>AI-powered professional outreach application</small>
    </div>
    """,
    unsafe_allow_html=True
)
