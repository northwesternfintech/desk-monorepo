from pysrc.util.slack_messenger import does_slack_user_exist
from pysrc.util.slack_utils import get_slack_id_by_name
from unittest.mock import patch, MagicMock


@patch("pysrc.util.slack_messenger._get_client")
def test_user_exists(mock_get_client: MagicMock) -> None:
    mock_client = mock_get_client.return_value

    mock_client.users_list.return_value = {
        "members": [
            {"id": "U123456", "profile": {"real_name": "Albert Einstein"}},
            {"id": "U123457", "profile": {"display_name": "Jimmy Neutron"}},
        ]
    }

    assert does_slack_user_exist("Albert Einstein") is True
    assert does_slack_user_exist("Jimmy Neutron") is True
    assert does_slack_user_exist("Christian Gonzales") is False


@patch("pysrc.util.slack_utils.get_user_if_valid")
@patch("pysrc.util.slack_messenger._get_client")
def test_get_slack_id_by_name_user_exists(
    mock_get_client: MagicMock, mock_get_user_if_valid: MagicMock
) -> None:
    mock_client = mock_get_client.return_value
    mock_get_user_if_valid.return_value = {
        "id": "U123456",
        "profile": {"real_name": "John Doe"},
    }

    slack_id = get_slack_id_by_name(mock_client, "John Doe", "user")

    assert slack_id == "U123456"
    mock_get_user_if_valid.assert_called_once_with(mock_client, "John Doe")


@patch("pysrc.util.slack_messenger._get_client")
def test_get_slack_id_by_name_channel_exists(mock_get_client: MagicMock) -> None:
    mock_client = mock_get_client.return_value
    mock_client.conversations_list.return_value = {
        "channels": [{"id": "C123456", "name": "general"}]
    }

    slack_id = get_slack_id_by_name(mock_client, "general", "channel")

    assert slack_id == "C123456"
    mock_client.conversations_list.assert_called_once_with(
        types="public_channel,private_channel"
    )


@patch("pysrc.util.slack_messenger._get_client")
def test_get_slack_id_by_name_channel_does_not_exist(
    mock_get_client: MagicMock,
) -> None:
    mock_client = mock_get_client.return_value
    mock_client.conversations_list.return_value = {"channels": []}

    slack_id = get_slack_id_by_name(mock_client, "nonexistent_channel", "channel")

    assert slack_id is None
    mock_client.conversations_list.assert_called_once_with(
        types="public_channel,private_channel"
    )
