from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

#currently designed to work for DeskBot only
desk_bot_token = os.getenv('DESK_BOT_TOKEN')

client = WebClient(token=desk_bot_token)

def format_mention(id: str):
    return f"<@{id}>" 

def send_slack_message(channel: str, message: str):
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print(f"Message sent to {channel}: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

test_message = format_mention("U03RN07KZHT") + " likes dick"
if __name__ == "__main__":
    send_slack_message(channel='#bot-test', message=test_message)
