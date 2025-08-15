import asyncio
import json
import os
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

crawler: Optional[AsyncWebCrawler] = None

async def initialize_crawler():
    global crawler
    if not crawler:
        crawler = AsyncWebCrawler(verbose=True)
        try:
            await crawler.astart()
        except AttributeError:
            pass

async def close_crawler():
    global crawler
    if crawler:
        try:
            await crawler.aclose()
        except AttributeError:
            pass

def google_search_urls(search_term: str, num_results: int = 5) -> List[str]:
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    query = search_term.replace(' ', '+')
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}&num={num_results}"

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return [item["link"] for item in data.get("items", [])]
    except Exception as e:
        print(f"Google Search error: {e}")
        return []

def get_timeout_links(search_term: str, max_links: int = 3) -> List[str]:
    encoded = search_term.replace(' ', '+')
    search_url = f"https://www.timeout.com/search?q={encoded}"
    try:
        resp = requests.get(search_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.select("a.card-content-link")[:max_links]:
            href = a.get("href")
            if href and not href.startswith("http"):
                href = "https://www.timeout.com" + href
            links.append(href)
        return links
    except Exception as e:
        print(f"Timeout extraction error: {e}")
        return []

def generate_travel_urls(search_term: str) -> List[str]:
    urls = google_search_urls(search_term)
    urls.extend(get_timeout_links(search_term))
    return urls

async def scrape_single_url(url: str, search_term: str) -> Optional[Dict]:
    try:
        print(f"Scraping: {url}")
        result = await crawler.arun(
            url=url,
            word_count_threshold=50,
            bypass_cache=True
        )
        if result.success and result.markdown:
            content = clean_content(result.html or result.markdown)
            if content:
                return {
                    "url": url,
                    "content": content,
                    "search_term": search_term,
                    "title": getattr(result, 'title', 'Travel Information')
                }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
    return None

def clean_content(html_or_md: str) -> str:
    soup = BeautifulSoup(html_or_md, "html.parser")
    main_content = soup.find("main") or soup.find("article") or soup
    lines = [line.strip() for line in main_content.get_text().split("\n") if len(line.strip()) > 20]
    skip_keywords = ['cookie', 'privacy', 'subscribe', 'newsletter', 'advertisement']
    cleaned_lines = [line for line in lines if not any(k in line.lower() for k in skip_keywords)]
    return "\n".join(cleaned_lines[:50])

async def scrape_simple_content(search_term: str, max_sites: int = 5) -> List[Dict]:
    if not crawler:
        await initialize_crawler()
    
    travel_urls = generate_travel_urls(search_term)
    tasks = [scrape_single_url(url, search_term) for url in travel_urls[:max_sites]]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r]

async def scrape_travel_data(search_terms: List[str]) -> List[Dict]:
    all_data = []
    try:
        await initialize_crawler()
        for term in search_terms:
            print(f"Processing search term: {term}")
            data = await scrape_simple_content(term)
            all_data.extend(data)
    finally:
        await close_crawler()
    return all_data

# Test run
async def test_scraper_full():
    search_terms = ["Canada things to do", "Toronto attractions"]
    data = await scrape_travel_data(search_terms)

    for item in data:
        print(f"URL: {item['url']}")
        print(f"Title: {item.get('title', 'No title')}")
        print("Full Content:")
        print(item['content'])
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(test_scraper_full())
