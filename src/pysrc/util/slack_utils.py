from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_slack_id_by_name(client, name, search_type="user"):
    """
    Retrieves the Slack ID for a user or channel by name.
    
    :param name: The name of the user (real or display) or the channel.
    :param search_type: Either "user" or "channel" to specify the type of search.
    :return: The user ID or channel ID, or None if not found.
    """
    try:
        if search_type == "user":
            # Fetch all users
            response = client.users_list()
            users = response['members']

            # Search for user by display name or real name
            for user in users:
                if user['profile']['display_name'] == name or user['profile']['real_name'] == name:
                    return user['id']  # Return the user's ID
            print(f"No user found with the name: {name}")
        
        elif search_type == "channel":
            # Fetch all channels (public and private)
            response = client.conversations_list(types="public_channel,private_channel")
            channels = response['channels']

            # Search for channel by name
            for channel in channels:
                if channel['name'] == name:
                    return channel['id']  # Return the channel's ID
            print(f"No channel found with the name: {name}")
        
        else:
            print("Invalid search type. Please use 'user' or 'channel'.")
        
        return None

    except SlackApiError as e:
        print(f"Error retrieving data: {e.response['error']}")
        return None

