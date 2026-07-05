import os
import chromadb
from dotenv import load_dotenv
from openai import AsyncOpenAI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
aclient = AsyncOpenAI()

api_key = os.getenv("OPENAI_API_KEY")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

reader = PdfReader('sample_resume.pdf')
extracted_text = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        extracted_text += text
        
chunked_text = text_splitter.split_text(extracted_text)

openai_ef = OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name='text-embedding-3-small'
)

client = chromadb.PersistentClient(path="./document_vector")
collection = client.get_or_create_collection(name="pdf_resumes", embedding_function=openai_ef)

initial_id = []
initial_id_count = 0
metadata=[]
for each_text in chunked_text:
    initial_id_count += 1 
    initial_id.append(f"chunk_{initial_id_count}")
    metadata.append({'source':"sample_resume.pdf"})

collection.upsert(
    documents= chunked_text,
    ids=initial_id,
    metadatas=metadata
)

print(f'Total chunks in database: {collection.count()}')