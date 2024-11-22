from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

_users: Optional[list[dict]] = None


def _get_users(client: WebClient) -> Optional[list[dict]]:
    global _users
    if _users is None:
        _users = client.users_list().get("members", [])
    return _users


def get_user_if_valid(client: WebClient, name: str) -> Optional[dict]:
    users = _get_users(client)
    if not users:
        print(
            "Could not retreieve list of slack users (is the WebClient working properly?)"
        )
        return None
    for user in users:
        profile = user.get("profile", {})
        if profile.get("display_name") == name or profile.get("real_name") == name:
            return user
    return None


def get_slack_id_by_name(
    client: WebClient, name: str, search_type: str = "user"
) -> Optional[str]:
    try:
        if search_type == "user":
            user = get_user_if_valid(client, name)
            if user:
                return str(user["id"])
            print(f"No user found with the name: {name}")

        elif search_type == "channel":
            response = client.conversations_list(types="public_channel,private_channel")
            channels: list[dict] = response.get("channels", [])

            for channel in channels:
                if channel.get("name") == name:
                    return str(channel["id"])
            print(f"No channel found with the name: {name}")

        else:
            print("Invalid search type. Please use 'user' or 'channel'.")

        return None

    except SlackApiError as e:
        print(f"Error retrieving data: {e.response['error']}")
        return None
