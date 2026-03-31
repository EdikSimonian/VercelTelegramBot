from unittest.mock import patch, MagicMock


def make_tavily_response(results):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"results": results}
    return mock_resp


def test_web_search_returns_formatted_results():
    results = [
        {"title": "Python Docs", "content": "Official docs", "url": "https://python.org"},
        {"title": "Real Python", "content": "Tutorials", "url": "https://realpython.com"},
    ]
    with patch("bot.search.requests.post", return_value=make_tavily_response(results)):
        from bot.search import web_search
        output = web_search("python tutorials")
        assert "Python Docs" in output
        assert "https://python.org" in output
        assert "Real Python" in output


def test_web_search_no_results():
    with patch("bot.search.requests.post", return_value=make_tavily_response([])):
        from bot.search import web_search
        assert web_search("xkqzwmf") == "No results found."


def test_web_search_sends_correct_payload():
    with patch("bot.search.requests.post", return_value=make_tavily_response([])) as mock_post:
        from bot.search import web_search
        web_search("test query")
        payload = mock_post.call_args[1]["json"]
        assert payload["query"] == "test query"
        assert payload["max_results"] == 5
