import pytest

from pysrc.util.slack_utils import (
    get_user_if_valid,
    get_slack_id_by_name,
)
from unittest.mock import patch, MagicMock
from slack_sdk.web.client import WebClient


@patch("pysrc.util.slack_utils._get_users")
def test_get_user_if_valid(mock_get_users: MagicMock) -> None:
    mock_users = [
        {
            "id": "U12345",
            "profile": {
                "display_name": "alice",
                "real_name": "Alice Smith",
            },
        },
        {
            "id": "U67890",
            "profile": {
                "display_name": "bob",
                "real_name": "Bob Jones",
            },
        },
    ]

    mock_get_users.return_value = mock_users
    mock_client = MagicMock(spec=WebClient)

    result = get_user_if_valid(mock_client, "alice")
    expected_user = mock_users[0]
    assert result == expected_user

    result = get_user_if_valid(mock_client, "Bob Jones")
    expected_user = mock_users[1]
    assert result == expected_user

    result = get_user_if_valid(mock_client, "charlie")
    assert result is None

    mock_get_users.return_value = []
    result = get_user_if_valid(mock_client, "alice")
    assert result is None


@patch("pysrc.util.slack_utils._get_users")
def test_get_slack_id_by_name(mock_get_users: MagicMock) -> None:
    # Test user search
    mock_users = [
        {
            "id": "U12345",
            "profile": {
                "display_name": "alice",
                "real_name": "Alice Smith",
            },
        },
        {
            "id": "U67890",
            "profile": {
                "display_name": "bob",
                "real_name": "Bob Jones",
            },
        },
    ]

    mock_get_users.return_value = mock_users
    mock_client = MagicMock(spec=WebClient)

    result = get_slack_id_by_name(mock_client, "alice")
    assert result == "U12345"

    result = get_slack_id_by_name(mock_client, "Bob Jones")
    assert result == "U67890"

    result = get_slack_id_by_name(mock_client, "charlie")
    assert result is None

    mock_get_users.return_value = []
    result = get_slack_id_by_name(mock_client, "alice")
    assert result is None

    # Test channel search
    mock_channels = [
        {
            "id": "C12345",
            "name": "general",
        },
        {
            "id": "C67890",
            "name": "random",
        },
    ]

    mock_client.conversations_list.return_value = {"channels": mock_channels}

    result = get_slack_id_by_name(mock_client, "general", search_type="channel")
    assert result == "C12345"

    result = get_slack_id_by_name(mock_client, "random", search_type="channel")
    assert result == "C67890"

    result = get_slack_id_by_name(mock_client, "invalid", search_type="channel")
    assert result is None

    mock_client.conversations_list.return_value = {}
    result = get_slack_id_by_name(mock_client, "general", search_type="channel")
    assert result is None

    # Test invalid search type
    result = get_slack_id_by_name(mock_client, "general", search_type="invalid")
    assert result is None
