import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb import PersistentClient

load_dotenv()

api_key= os.getenv("OPENAI_API_KEY")
ai_client = OpenAI()

openai_ef = OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-small"
)

db_client = PersistentClient(path='./document_vector')
collection = db_client.get_or_create_collection(name="pdf_resumes", embedding_function=openai_ef)

results = collection.query(
    query_texts=["Summarize the candidate's work history and education."],
    n_results= 3
)

combined_context = ""
chunks = results["documents"][0]
source = results['metadatas'][0][0]['source']

for i, chunk in enumerate(chunks):
    combined_context+= f"\n--- CHUNK {i+1} ---\n{chunk}\n"
    
print("Stitched Context looks like this:\n", combined_context)

system_prompt = f'''You are an HR assistant.
Answer the user's question using ONLY the provided context chunks.
Synthesize the information into a cohesive summary.

Context : {combined_context}
Source : {source}
'''

def call_ai(system_text):
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content":system_text},
                {"role":"user", "content":"Summarize the candidate's work history and education."}
            ])
        ai_response = response.choices[0].message.content
        return ai_response
        
    except Exception as err:
        print(f"ERROR: {err}")
        
ai_answer = call_ai(system_prompt)
print(ai_answer)