#!/usr/bin/env python
# coding: utf-8

# In[1]:


from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0,
    groq_api_key='add the key',  # Replace this with your real key
    model_name="llama3-70b-8192"  # Correct model name
)

response = llm.invoke("The first person to land on the moon was ...")
print(response.content)


# In[3]:


from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://internshala.com/job/detail/fresher-remote-junior-data-scientist-job-at-mediacom-india1753532936")
page_data = loader.load().pop().page_content
print(page_data)


# In[5]:


from langchain_core.prompts import PromptTemplate

prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing the 
        following keys: `role`, `experience`, `skills` and `description`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):    
        """
)

chain_extract = prompt_extract | llm 
res = chain_extract.invoke(input={'page_data':page_data})
type(res.content)


# In[9]:


from langchain_core.output_parsers import JsonOutputParser

json_parser = JsonOutputParser()
json_res = json_parser.parse(res.content)
json_res


# In[11]:


type(json_res)


# In[25]:


import pandas as pd

df = pd.read_csv("my_portfolio.csv")
df


# In[27]:


import uuid
import chromadb

client = chromadb.PersistentClient('vectorstore')
collection = client.get_or_create_collection(name="portfolio")

if not collection.count():
    for _, row in df.iterrows():
        collection.add(documents=row["Techstack"],
                       metadatas={"links": row["Links"]},
                       ids=[str(uuid.uuid4())])


# In[35]:


# 1. Get job entry from parsed JSON
job = json_res[0]
# 2. Query ChromaDB using job['skills']
links = collection.query(query_texts=job['skills'], n_results=2).get('metadatas', [])
print(links)


# In[37]:


job


# In[41]:


job = json_res[0]  #  get the first job dictionary
print(job['skills'])


# In[53]:


prompt_email = PromptTemplate.from_template(
        """
     ### JOB DESCRIPTION:
        {job_description}
        
        ### INSTRUCTION:
        You are Mohan, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
        the seamless integration of business processes through automated tools. 
        Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
        process optimization, cost reduction, and heightened overall efficiency. 
        Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
        in fulfilling their needs.
        Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
        Remember you are Mohan, BDE at AtliQ. 
        Do not provide a preamble.
        ### EMAIL (NO PREAMBLE):
        """
        )

chain_email = prompt_email | llm
res = chain_email.invoke({"job_description": str(job), "link_list": links})
print(res.content)


# In[ ]:




