from slack_sdk.errors import SlackApiError
from typing import Optional
from slack_sdk import WebClient

def get_slack_id_by_name(client: WebClient, name: str, search_type: str = "user") -> Optional[str]:

    try:
        if search_type == "user":
            response = client.users_list()
            users = response['members']

            for user in users:
                if user['profile']['display_name'] == name or user['profile']['real_name'] == name:
                    return user['id']
            print(f"No user found with the name: {name}")
        
        elif search_type == "channel":
            response = client.conversations_list(types="public_channel,private_channel")
            channels = response['channels']

            for channel in channels:
                if channel['name'] == name:
                    return channel['id']
            print(f"No channel found with the name: {name}")
        
        else:
            print("Invalid search type. Please use 'user' or 'channel'.")
        
        return None

    except SlackApiError as e:
        print(f"Error retrieving data: {e.response['error']}")
        return None

