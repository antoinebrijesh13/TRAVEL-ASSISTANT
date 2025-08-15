from dataclasses import dataclass
from typing import Optional
import requests
import json


@dataclass
class TravelQuery:
    destination: str
    activity_type: Optional[str] = None
    duration: Optional[str] = None
    budget: Optional[str] = None
    interests: list = None  
def parse_with_ollama(query: str) -> TravelQuery:
    """Parse using local Ollama LLM"""
    try:
        
        prompt = f"""Extract travel information from this query and return ONLY a JSON object with these fields:
{{
    "destination": "extracted destination or null",
    "activity_type": "food/culture/outdoor/nightlife/shopping/business or null", 
    "duration": "extracted duration or null",
    "budget": "extracted budget or null",
    "interests": ["list", "of", "interests"] or null
}}

Query: "{query}"

JSON:"""

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:latest', 
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'top_p': 0.9,
                    'num_predict': 200
                }
            },
            timeout=60  
        )
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start = result.find('{')
                end = result.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = result[start:end]
                    extracted = json.loads(json_str)
                    
                    return TravelQuery(
                        destination=extracted.get('destination'),
                        activity_type=extracted.get('activity_type'),
                        duration=extracted.get('duration'),
                        budget=extracted.get('budget'),
                        interests=extracted.get('interests')
                    )
            except json.JSONDecodeError:
                pass
                
    except Exception as e:
        print(f"Ollama parsing error: {e}")
    
    # If LLM fails, fall back to rule-based
    raise Exception("LLM parsing failed")

def generate_search_terms(travel_query:TravelQuery)-> list:
    searchterms = []
    if travel_query.destination:
        base_terms = [
            f"{travel_query.destination} things to do",
            f"{travel_query.destination} attractions",
            f"{travel_query.destination} travel guide",
            f"visit {travel_query.destination}"
        ]
        searchterms.extend(base_terms) 
        if travel_query.activity_type:
            searchterms.append(f"{travel_query.destination} {travel_query.activity_type}")
        
        if travel_query.interests:
            for interest in travel_query.interests:
                searchterms.append(f"{travel_query.destination} {interest}")
    
    return searchterms     


#test
if __name__ == "__main__":
    test_query = "I want to go to Paris for 5 days to explore museums and art galleries and i can only spend 100 dollars" \
    "."
    try:
        parsed_query = parse_with_ollama(test_query)
        print(parsed_query)
    except Exception as e:
        print(f"Parsing error: {e}")