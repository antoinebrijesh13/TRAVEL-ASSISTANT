import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from typing import List,Dict
from langchain_community.vectorstores import FAISS
import json
from datetime import datetime

vectorstore = None
embeddings =  None
llm = None
texsplitter = None

def initialize():
    global vectorstore,embeddings,llm,texsplitter

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    embeddings=GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        api_key=api_key,
    )
    
    texsplitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    try:
        load_vectorstore()
    except:
        print("no existing vector db, creating new one ....")
  
#Add scraped travel documents to the vector database
def add_travel_documents(scraped_data: List[Dict]):
    global vectorstore,embeddings

    documents = []

    for item in scraped_data:
        content = item.get('content', '')
        metadata = {
                "source": item.get('url', ''),
                "search_term": item.get('search_term', ''),
                "title": item.get('title', ''),
                "type": "raw_content",
                "timestamp": datetime.now().isoformat()
            }
        if content and len(content.strip()) > 50:  # Only add meaningful content
            documents.append(Document(page_content=content, metadata=metadata))
    if documents:
        if vectorstore is None:
            vectorstore = FAISS.from_documents(documents,embeddings)
            print(f"Created new vector data base with {len(documents)}documents")
        vectorstore.add_documents(documents)
        print(f"Added {len(documents)} documents to existing vector database")

#querying
def search_relevant_info(query:str,k:int=5)->List[Dict]:
    global vectorstore

    if vectorstore is None:
        return[]
    results = vectorstore.similarity_search_with_score(query,k=k)

    return[
        {"content": doc.page_content,
        "metadata": doc.metadata,
        "relevance_score": float(score)
        }
        for doc,score in results
    ]

#Check if sufficient information is available for a query
def check_information_availability(query: str, threshold: float = 0.8) -> tuple[bool, List[Dict]]:
    results = search_relevant_info(query, k=5)
    
    if not results:
        return False, []
    relevant_results = [r for r in results if r['relevance_score'] < threshold]
    
    # Calculate content quality - ensure we have substantial content
    total_content_length = sum(len(r['content']) for r in relevant_results)
    
    # We have sufficient info if:
    # 1. At least 2 relevant results with good similarity scores
    # 2. Combined content is substantial (at least 500 characters)
    if len(relevant_results) >= 2 and total_content_length >= 500:
        return True, relevant_results
    
    return False, results

 #Save the vector database
def save_vectorstore(path: str = "travel_vectordb"):
   
    global vectorstore
    
    if vectorstore:
        vectorstore.save_local(path)
        print(f"Vector database saved to {path}")
#load the vector database
def load_vectorstore(path: str = "travel_vectordb"):
    global vectorstore, embeddings
    
    if embeddings is None:
        raise ValueError("Please initialize the system first by calling initialize()")
    
    try:
        vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        return True
    except Exception as e:
        print(f"Could not load vectordb from {path}: {e}")
        return False
#clear vectordatabase
def clear_database():
    global vectorstore
    vectorstore = None
    print("Vector database cleared")