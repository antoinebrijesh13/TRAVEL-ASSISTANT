# TRAVEL ASSISTANT

A Python-based travel assistant that helps users plan trips, gather information, and manage travel data using vector databases and web crawling.

## Features
- Query parsing for travel-related questions
- Web crawling to gather travel information
- Vector database for efficient information retrieval
- Modular Python codebase

## Project Structure
- `Travel_Assistant.py`: Main application logic
- `GENERATIONLLM.py`: Language model generation utilities
- `QUERYPARSER.py`: Query parsing logic
- `VECTORDB.py`: Vector database management
- `WEBCRAWLER.py`: Web crawling utilities
- `travel_vectordb/`: Stores vector database files
- `.env`: Environment variables (not tracked by git)

## Getting Started
1. Clone the repository:
   ```sh
   git clone https://github.com/antoinebrijesh13/TRAVEL-ASSISTANT.git
   ```
2. Install dependencies (see below).
3. Set up your `.env` file with required environment variables.
4. Run the main script:
   ```sh
   python Travel_Assistant.py
   ```

## Dependencies
- Python 3.10+
- (Add any additional dependencies here)

## Environment Variables
Create a `.env` file in the root directory and add your keys/configuration:
```
API_KEY=your_api_key_here
OTHER_CONFIG=your_config
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)
