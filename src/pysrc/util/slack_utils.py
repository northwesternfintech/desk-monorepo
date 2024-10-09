from slack_sdk.errors import SlackApiError
from typing import Optional
from slack_sdk import WebClient

def get_slack_id_by_name(client: WebClient, name: str, search_type: str = "user") -> Optional[str]:
    try:
        if search_type == "user":
            response = client.users_list()
            users = response.get('members', [])

            for user in users:
                # Ensure the 'profile' key exists in the user dictionary
                profile = user.get('profile', {})
                if profile.get('display_name') == name or profile.get('real_name') == name:
                    return user['id']
            print(f"No user found with the name: {name}")

        elif search_type == "channel":
            response = client.conversations_list(types="public_channel,private_channel")
            channels = response.get('channels', [])

            for channel in channels:
                if channel.get('name') == name:
                    return channel['id']
            print(f"No channel found with the name: {name}")

        else:
            print("Invalid search type. Please use 'user' or 'channel'.")

        return None

    except SlackApiError as e:
        print(f"Error retrieving data: {e.response['error']}")
        return None

