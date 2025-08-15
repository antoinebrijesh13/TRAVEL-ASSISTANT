from VECTORDB import search_relevant_info
from typing import List, Dict
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI

#Generate travel response using available information"""
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
def generate_travel_response(query: str, context_docs: List[Dict] = None) -> str:
    
    if llm is None:
        raise ValueError("Please initialize the system first by calling initialize()")
    
    if context_docs is None:
        context_docs = search_relevant_info(query, k=3)
    
    if not context_docs:
        return "I don't have specific information about that destination yet. Let me gather some information for you."
    
    context = "\n\n".join([doc["content"] for doc in context_docs[:3]])
    
    prompt = f"""
    Based on the following travel information, provide a helpful and engaging response to the user's travel query.
    Focus on specific attractions, activities, and practical travel advice.

    Travel Information:
    {context}

    User Query: {query}

    Please provide a comprehensive but concise response about things to do, places to visit, and travel tips.
    Format your response in a friendly, informative way.
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I found some information but had trouble processing it. Please try again."