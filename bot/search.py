import requests
from bot.config import TAVILY_API_KEY

TAVILY_ENDPOINT = "https://api.tavily.com/search"


def web_search(query: str, count: int = 5) -> str:
    """Search the web via Tavily API and return formatted results."""
    response = requests.post(
        TAVILY_ENDPOINT,
        json={"api_key": TAVILY_API_KEY, "query": query, "max_results": count},
        timeout=10,
    )
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        return "No results found."

    return "\n\n".join(
        f"{r['title']}\n{r.get('content', '')}\n{r['url']}"
        for r in results
    )
