import logging
import os
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from pysrc.util.slack_utils import get_slack_id_by_name, get_user_if_valid
from pysrc.util.system import get_current_user_slack_name

SPECIAL_MENTIONS = ("here", "everyone", "channel")

_client: Optional[WebClient] = None
_logger = logging.getLogger(__name__)


def _get_client() -> WebClient:
    global _client
    if _client is None:
        desk_bot_token = os.getenv("DESK_BOT_TOKEN")
        if not desk_bot_token:
            raise OSError(
                "The environment variable 'DESK_BOT_TOKEN' is not set. Please set it before running the script."
            )
        _client = WebClient(token=desk_bot_token)
    return _client


def _format_mention(id: str) -> str:
    if not id:
        raise AssertionError("ID cannot be an empty string")

    if id in ["channel", "here", "everyone"]:
        return f"<!{id}>"

    assert id[0] == "U" or id[0] == "C"
    if id[0] == "U":
        return f"<@{id}>"  # Mention user
    return f"<#{id}>"  # Mention channel


def send_slack_message(channel: str, message: str, mentions: list[str] = []) -> None:
    client = _get_client()
    result_message = ""
    for mention in mentions:
        mention_id = (
            get_slack_id_by_name(client, mention)
            if mention not in SPECIAL_MENTIONS
            else mention
        )
        if not mention_id:
            raise AssertionError("ID cannot be None")
        result_message += _format_mention(mention_id)
    result_message += message
    try:
        response = client.chat_postMessage(channel=channel, text=result_message)
        _logger.debug(f"Message sent to {channel}: {response['ts']}")
    except SlackApiError as e:
        _logger.warning(f"Error sending message: {e.response['error']}")


def send_slack_message_to_current_server_user(channel: str, message: str) -> None:
    slack_user = get_current_user_slack_name()
    send_slack_message(channel, message, [slack_user])


def does_slack_user_exist(name: str) -> bool:
    client = _get_client()
    return get_user_if_valid(client, name) is not None
