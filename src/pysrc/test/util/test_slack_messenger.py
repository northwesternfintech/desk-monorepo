import pytest

from pysrc.util.slack_messenger import _format_mention

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


