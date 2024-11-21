from unittest.mock import MagicMock, patch

import pytest

from pysrc.util.slack_messenger import (
    _format_mention,
    send_slack_message_to_current_server_user,
)


def test_format_mention_special_mentions() -> None:
    assert _format_mention("channel") == "<!channel>"
    assert _format_mention("here") == "<!here>"
    assert _format_mention("everyone") == "<!everyone>"


def test_format_mention_user_id() -> None:
    assert _format_mention("U123456") == "<@U123456>"


def test_format_mention_channel_id() -> None:
    assert _format_mention("C123456") == "<#C123456>"


def test_format_mention_invalid_input() -> None:
    with pytest.raises(AssertionError):
        _format_mention("invalid_id")

    with pytest.raises(AssertionError):
        _format_mention("X123456")

    with pytest.raises(AssertionError):
        _format_mention("")


@patch("pysrc.util.system.get_current_user")
@patch("pysrc.util.slack_messenger.send_slack_message")
def test_send_messsage_to_current_server_user(
    mock_send_slack_message: MagicMock, mock_get_current_user: MagicMock
) -> None:
    mock_get_current_user.return_value = "mglass"
    send_slack_message_to_current_server_user("general", "hello")
    mock_send_slack_message.assert_called_once_with("general", "hello", ["Max Glass"])
