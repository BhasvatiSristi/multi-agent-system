from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from rich import print
import os
from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Perform a web search and return the top results."""
    try:
        results = tavily.search(query=query, max_results=5)
        output=[]
        for r in results['results']:
            output.append(
                f"Title: {r['title']}\n"
                f"URL: {r['url']}\n"
                f"content: {r['content'][:300]}\n"
            )
        return "\n----\n".join(output)

    except Exception as e:
        return f"Error performing web search: {str(e)}"

@tool
def web_scrape(url: str) -> str:
    """Scrape the content of a web page."""
    try:
        response = requests.get(url,timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style','nav','footer']):
            tag.decompose()
        return soup.get_text(separator=' ',strip=True)[:3000]
    except Exception as e:
        return f"Error scraping web page: {str(e)}"

results=web_scrape.invoke("https://www.weatherapi.com/")
print(results)