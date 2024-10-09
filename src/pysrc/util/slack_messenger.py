from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack_utils import get_slack_id_by_name
import os

desk_bot_token = os.getenv('DESK_BOT_TOKEN')

if not desk_bot_token:
    raise EnvironmentError("The environment variable 'DESK_BOT_TOKEN' is not set. Please set it before running the script.")

client = WebClient(token=desk_bot_token)

def _format_mention(id: str) -> str:
    if not id:
        raise AssertionError("ID cannot be an empty string")

    if id in ["channel", "here", "everyone"]:
        return f"<!{id}>"
    
    assert(id[0] == "U" or id[0] == "C")
    if id[0] == "U":
        return f"<@{id}>"  # Mention user
    return f"<#{id}>"  # Mention channel

def send_slack_message(channel: str, message: str, mentions: list[str] = []) -> None:
    result_message = ""
    for mention in mentions:
        mention_id = get_slack_id_by_name(client, mention) if mention not in ["here", "everyone", "channel"] else mention 
        result_message+=_format_mention(mention_id)
    result_message+=message
    try:
        response = client.chat_postMessage(channel=channel, text=result_message)
        print(f"Message sent to {channel}: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
