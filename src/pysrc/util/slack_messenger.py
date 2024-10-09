from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
#from slack_utils import get_slack_id_by_name
import os

#currently designed to work for DeskBot only
desk_bot_token = os.getenv('DESK_BOT_TOKEN')

if not desk_bot_token:
    raise EnvironmentError("The environment variable 'DESK_BOT_TOKEN' is not set. Please set it before running the script.")

client = WebClient(token=desk_bot_token)

def format_mention(id: str):
    if id in ["channel", "here", "everyone"]:
        return f"<!{id}>"
    
    assert(id[0] == "U" or id[0] == "C")
    if id[0] == "U":
        return f"<@{id}>"  # Mention user
    return f"<#{id}>"  # Mention channel

def send_slack_message(channel: str, message: str):
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print(f"Message sent to {channel}: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

test_message = format_mention("here") + " likes apples!"
if __name__ == "__main__":
    send_slack_message(channel='#bot-test', message=test_message)
