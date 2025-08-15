import asyncio
import os
from typing import Dict,Optional,List,Tuple
from dotenv import load_dotenv

#modules
import VECTORDB
from QUERYPARSER import parse_with_ollama,generate_search_terms
from WEBCRAWLER import scrape_travel_data
from GENERATIONLLM import generate_travel_response
load_dotenv()

_api_key = None
_initilized = False

def set_api_key(api_key:str=None)->None:
    global _api_key
    _api_key = api_key or os.getenv("OPENAI_API_KEY")
    return _api_key
def initialize():
    global _initilized
    
    try:
        VECTORDB.initialize()
        print("vector database initialized")
        _initilized = True
        print("everythings ready!")
        return True
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return False

def is_initilized()->bool:
    return _initilized
#process query with ollama
async def process_query(user_query:str)->str:
    #1.parse the user quey
    print(f"Processing query: {user_query}")
    parsed_query = parse_with_ollama(user_query)
    if not parsed_query.destination:
        return "I couldn't identify a specific destination from your query. Could you please mention where you'd like to travel?"
    #2.check wxisting information in vector db
    hasinfo,existing_results = VECTORDB.check_information_availability(user_query)
    if hasinfo:
        print("Found sufficient information in the Data base using existing data")
        response = generate_travel_response(user_query,existing_results)
        return response
    #3.we scrape for more data
    print("I cannot find enough information in the vector database. Let me gather some more data for you.")
    search_terms = generate_search_terms(parsed_query)
    print(f"search terms: {search_terms}")

    #4.Scrape new information
    scraped = await scrape_travel_data(search_terms[:2])

    #5.add scraped information to vector db
    if scraped:
        VECTORDB.add_travel_documents(scraped)
        print(f"Added {len(scraped)} new documents to the vector database")

        VECTORDB.save_vectorstore()
    #6.generate response with new information
        response = generate_travel_response(user_query)
        return response
    return f"I wasn't able to find comprehensive information about {parsed_query.destination} right now. Please try again later or be more specific about what you'd like to know."


async def process_travel_query(user_query:str)->str:
    if not _initilized:
        if not initialize:
            return "Travel Assistant is not initialized."
    return await process_query(user_query)

def clear_database():
    VECTORDB.clear_database()
    print("Database cleared")

def print_welcome_message():
    print(" Welcome to Travel Assistant!")
    print("Ask me anything about travel destinations.")
    print("Type 'quit' to exit, 'clear' to clear database")
    print("-" * 60)

def parse_cli_command(user_input: str) -> Tuple[str, Optional[List[str]]]:
    """Parse CLI command and return command type and parameters"""
    user_input = user_input.strip().lower()
    
    if user_input in ['quit', 'exit', 'q']:
        return 'quit', None
    elif user_input == 'clear':
        return 'clear', None
    else:
        return 'query', None

async def handle_cli_command(command: str, params: Optional[List[str]], original_input: str) -> bool:
    
    if command == 'quit':
        print(" Thanks for using Travel Assistant!")
        return False

    
    elif command == 'clear':
        clear_database()
        return True

    elif command == 'query':
        print("\n🔍 Processing your query...")
        response = await process_travel_query(original_input)
        print(f"\n Travel Assistant says:\n{response}")
        print("-" * 60)
        return True
    
    return True

async def run_interactive_cli():
    print_welcome_message()
    
    if not initialize():
        return
    
    running = True
    while running:
        try:
            user_input = input("\nYour travel question: ").strip()
            
            if not user_input:
                continue
            
            command, params = parse_cli_command(user_input)
            running = await handle_cli_command(command, params, user_input)
            
        except KeyboardInterrupt:
            print("\nThanks for using Travel Assistant!")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Cleanup before exit
    await asyncio.sleep(0.2)
async def get_travel_advice(query: str) -> str:
    """Simple function to get travel advice"""
    set_api_key()
    return await process_travel_query(query, use_crew=False)

def main():
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
        async def run_single_query():
            response = await get_travel_advice(query)
            print(response)
        
        asyncio.run(run_single_query())
    else:
        # Interactive CLI
        asyncio.run(run_interactive_cli())

# Main execution
if __name__ == "__main__":
    main()
