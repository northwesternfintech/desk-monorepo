import os

import pytest

from pysrc.util.slack_messenger import does_slack_user_exist
from pysrc.util.slack_utils import get_slack_id_by_name
from pysrc.util.system import SERVER_USERNAME_TO_SLACK_NAME


@pytest.mark.skipif(
    os.getenv("DESK_BOT_TOKEN") is None, reason="DESK_BOT_TOKEN not set"
)
def test_server_username_to_slack_name_valid_slack_names() -> None:
    for slack_name in SERVER_USERNAME_TO_SLACK_NAME.values():
        assert does_slack_user_exist(slack_name) is True
