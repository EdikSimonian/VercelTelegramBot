from unittest.mock import patch, MagicMock


def make_brave_response(results):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"web": {"results": results}}
    return mock_resp


def test_web_search_returns_formatted_results():
    results = [
        {"title": "Python Docs", "description": "Official docs", "url": "https://python.org"},
        {"title": "Real Python", "description": "Tutorials", "url": "https://realpython.com"},
    ]
    with patch("bot.search.requests.get", return_value=make_brave_response(results)):
        from bot.search import web_search
        output = web_search("python tutorials")
        assert "Python Docs" in output
        assert "https://python.org" in output
        assert "Real Python" in output


def test_web_search_no_results():
    with patch("bot.search.requests.get", return_value=make_brave_response([])):
        from bot.search import web_search
        assert web_search("xkqzwmf") == "No results found."


def test_web_search_uses_strict_safesearch():
    with patch("bot.search.requests.get", return_value=make_brave_response([])) as mock_get:
        from bot.search import web_search
        web_search("test query")
        params = mock_get.call_args[1]["params"]
        assert params["safesearch"] == "strict"
