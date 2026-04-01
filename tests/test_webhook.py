from unittest.mock import patch, MagicMock


def test_webhook_rejects_bad_secret():
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "wrong_secret"
    mock_request.get_data.return_value = "{}"
    with patch("api.index.WEBHOOK_SECRET", "correct_secret"), \
         patch("api.index.request", mock_request), \
         patch("api.index.bot"):
        from api.index import webhook
        result = webhook()
        assert result == ("Forbidden", 403)


def test_webhook_accepts_correct_secret():
    mock_request = MagicMock()
    mock_request.headers.get.return_value = "correct_secret"
    mock_request.get_data.return_value = "{}"
    with patch("api.index.WEBHOOK_SECRET", "correct_secret"), \
         patch("api.index.request", mock_request), \
         patch("api.index.bot"), \
         patch("api.index.telebot") as mock_telebot:
        mock_telebot.types.Update.de_json.return_value = MagicMock()
        from api.index import webhook
        result = webhook()
        assert result == ("OK", 200)


def test_webhook_skips_validation_when_no_secret():
    mock_request = MagicMock()
    mock_request.get_data.return_value = "{}"
    with patch("api.index.WEBHOOK_SECRET", ""), \
         patch("api.index.request", mock_request), \
         patch("api.index.bot"), \
         patch("api.index.telebot") as mock_telebot:
        mock_telebot.types.Update.de_json.return_value = MagicMock()
        from api.index import webhook
        result = webhook()
        assert result == ("OK", 200)
