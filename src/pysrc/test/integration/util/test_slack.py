from pysrc.util.slack_messenger import does_slack_user_exist
import pytest
import os

@pytest.mark.skipif(os.getenv("DESK_BOT_TOKEN") is None, reason="DESK_BOT_TOKEN not set")
def test_user_exists() -> None:

    assert does_slack_user_exist("Ethan Havemann") is True
    assert does_slack_user_exist("Aidan Villasenor") is True
    assert does_slack_user_exist("Christian Gonzales") is False
