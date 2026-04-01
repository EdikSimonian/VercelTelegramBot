from unittest.mock import patch, MagicMock
from bot.ai import needs_search


# ── needs_search ───────────────────────────────────────────────────────────────

def test_needs_search_detects_news():
    assert needs_search("what is the latest news about Iran?") is True


def test_needs_search_detects_today():
    assert needs_search("what happened today?") is True


def test_needs_search_detects_current():
    assert needs_search("who is the current president?") is True


def test_needs_search_false_for_general_question():
    assert needs_search("what is the capital of France?") is False


def test_needs_search_false_for_coding_question():
    assert needs_search("how do I reverse a list in Python?") is False


def test_needs_search_case_insensitive():
    assert needs_search("What is TODAY's weather?") is True


# ── _call_ai retry logic ──────────────────────────────────────────────────────

def test_call_ai_retries_on_failure():
    mock_response = MagicMock()
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.time.sleep") as mock_sleep:
        mock_ai.chat.completions.create.side_effect = [
            Exception("network error"),
            mock_response,
        ]
        from bot.ai import _call_ai
        result = _call_ai([{"role": "user", "content": "hi"}])
        assert result == mock_response
        assert mock_ai.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once_with(1)


def test_call_ai_raises_after_max_retries():
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.time.sleep"):
        mock_ai.chat.completions.create.side_effect = Exception("persistent error")
        from bot.ai import _call_ai
        try:
            _call_ai([{"role": "user", "content": "hi"}], retries=3)
            assert False, "Should have raised"
        except Exception as e:
            assert str(e) == "persistent error"
        assert mock_ai.chat.completions.create.call_count == 3


def test_call_ai_succeeds_first_try():
    mock_response = MagicMock()
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.time.sleep") as mock_sleep:
        mock_ai.chat.completions.create.return_value = mock_response
        from bot.ai import _call_ai
        result = _call_ai([{"role": "user", "content": "hi"}])
        assert result == mock_response
        mock_sleep.assert_not_called()


# ── ask_ai orchestration ──────────────────────────────────────────────────────

def test_ask_ai_returns_reply():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello there!"
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.get_history", return_value=[]), \
         patch("bot.ai.save_history"):
        mock_ai.chat.completions.create.return_value = mock_response
        from bot.ai import ask_ai
        reply = ask_ai(123, "hi")
        assert reply == "Hello there!"


def test_ask_ai_saves_history():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "reply"
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.get_history", return_value=[]), \
         patch("bot.ai.save_history") as mock_save:
        mock_ai.chat.completions.create.return_value = mock_response
        from bot.ai import ask_ai
        ask_ai(123, "hi")
        mock_save.assert_called_once()
        saved_history = mock_save.call_args[0][1]
        assert saved_history[0] == {"role": "user", "content": "hi"}
        assert saved_history[1]["role"] == "assistant"


def test_ask_ai_appends_sources_when_search_used():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Here is the news."
    sources = [{"title": "BBC", "url": "https://bbc.com"}]
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.get_history", return_value=[]), \
         patch("bot.ai.save_history"), \
         patch("bot.ai.TAVILY_API_KEY", "fake_key"), \
         patch("bot.ai.needs_search", return_value=True), \
         patch("bot.search.web_search", return_value=("search text", sources)):
        mock_ai.chat.completions.create.return_value = mock_response
        from bot.ai import ask_ai
        reply = ask_ai(123, "latest news")
        assert "**Sources:**" in reply
        assert "[BBC](https://bbc.com)" in reply


def test_ask_ai_no_sources_for_general_question():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Paris."
    with patch("bot.ai.ai") as mock_ai, \
         patch("bot.ai.get_history", return_value=[]), \
         patch("bot.ai.save_history"):
        mock_ai.chat.completions.create.return_value = mock_response
        from bot.ai import ask_ai
        reply = ask_ai(123, "what is the capital of France?")
        assert "Sources" not in reply
