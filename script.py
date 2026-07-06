import os
from openai import OpenAI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb import PersistentClient
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

openai_client = OpenAI()

reader = PdfReader("sample_resume.pdf")
extracted_text = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        extracted_text+= text

chunked_text = text_splitter.split_text(extracted_text)

openai_ef = OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-small"
)

client = PersistentClient(path="./document_vector")
collection = client.get_or_create_collection(name="pdf_resumes", embedding_function=openai_ef)

initial_id_count = 0
initial_id = []
metadata = []
for chunk in chunked_text:
    initial_id_count += 1
    initial_id.append(f'chunk+{initial_id_count}')
    metadata.append({'source':'sample_resume.pdf'})

collection.upsert(
    documents=chunked_text,
    metadatas=metadata,
    ids=initial_id
)

results = collection.query(
    query_texts=["What are the candidate's customer service or canteen skills?"],
    n_results=1,
    where={'source':'sample_resume.pdf'}
    )

retrived_chunks = results["documents"][0][0]
retrived_source = results['metadatas'][0][0]['source']

system_prompt = f"""
You are an HR assistant. Answer the user's question using ONLY the provided context.
You MUST cite your source by explicitly mentioning the SOURCE FILE NAME in your answer.

CONTEXT: {retrived_chunks}
SOURCE FILE NAME: {retrived_source}
"""

def call_ai(system_message):
    try:
        response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system", "content":system_message},
                {"role":"user", "content":"What kind of customer service experience does this candidate have?"}])
        
        ai_said = response.choices[0].message.content
        return ai_said
        
    except Exception as err:
        print(f"Encountered {err}")

answer = call_ai(system_prompt)
print(answer)