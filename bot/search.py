import requests
from bot.config import BRAVE_API_KEY

BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


def web_search(query: str, count: int = 5) -> str:
    """Search the web via Brave Search API and return formatted results."""
    response = requests.get(
        BRAVE_ENDPOINT,
        headers={
            "X-Subscription-Token": BRAVE_API_KEY,
            "Accept": "application/json",
        },
        params={"q": query, "safesearch": "strict", "count": count},
        timeout=10,
    )
    response.raise_for_status()

    results = response.json().get("web", {}).get("results", [])
    if not results:
        return "No results found."

    return "\n\n".join(
        f"{r['title']}\n{r.get('description', '')}\n{r['url']}"
        for r in results
    )
