import pytest

from pysrc.util.slack_utils import (
    get_user_if_valid,
    get_slack_id_by_name,
)
from unittest.mock import MagicMock

def test_get_user_if_valid():
    client = MagicMock()
    client.users_list.return_value = {"members": [{"profile": {"display_name": "test", "real_name": "test"}}]}
    assert get_user_if_valid(client, "test") == {"profile": {"display_name": "test", "real_name": "test"}}

    client.users_list.return_value = {"members": [{"profile": {"display_name": "test", "real_name": "test"}}]}
    assert get_user_if_valid(client, "test2") == None

def test_get_slack_id_by_name():
    client = MagicMock()
    client.users_list.return_value = {"members": [{"profile": {"display_name": "test", "real_name": "test"}, "id": "U123456"}]}
    assert get_slack_id_by_name(client, "test") == "U123456"

    client.conversations_list.return_value = {"channels": [{"name": "test", "id": "C123456"}]}
    assert get_slack_id_by_name(client, "test", "channel") == "C123456"

    client.users_list.return_value = {"members": [{"profile": {"display_name": "test", "real_name": "test"}, "id": "U123456"}]}
    assert get_slack_id_by_name(client, "test2") == None

    client.conversations_list.return_value = {"channels": [{"name": "test", "id": "C123456"}]}
    assert get_slack_id_by_name(client, "test2", "channel") == None
