import socket
import getpass
from pysrc.util.types import Server
from pysrc.util.exceptions import DIE

SERVER_USERNAME_TO_SLACK_NAME: dict[str, str] = {
    "echavemann": "Ethan Havemann",
    "andrlime": "Andrew Li",
    "avillasenor": "Aidan Villasenor",
    "bhu": "Blake Hu",
    "dsl": "Daniel Lee",
    "efang": "Eddie Fang",
    "franklin": "Franklin Zhao",
    "gwang": "Gavin Wang",
    "jay": "Jay Park",
    "JCJR": "Jerry Cao",
    "jenny": "Jenny Zhou",
    "jerry": "Jerry Han",
    "john": "John Hileman",
    "mglass": "Max Glass",
    "minnce": "Chris Minn",
    "miya": "Miya Liu",
    "mmaiti": "Milind Maiti",
    "nikola": "Nino",
    "rewong": "Ryan Wong",
    "steev": "Steve Ewald",
    "fzhang": "Frank Zhang",
    "rmohan": "Romir Mohan",
    "myang": "Kevin Y",
    "nwangjs": "Nathan Wang",
    "hguan": "Harry Guan",
    "chengian": "Ian Cheng",
    "wu": "Nathan Wu",
    "maxbreslin": "Max Breslin",
    "nolenca": "Clayton Nolen",
    "ahuang9999": "Alex Huang",
    "xyliu": "Yang Liu",
    "mossbarger": "Luke Mossbarger",
    "jasonzhxn": "Jason Zhan",
    "wbrittian": "Will Brittian",
}


def get_current_server() -> Server:
    hostname = _get_current_server_hostname()
    return _hostname_to_enum(hostname)


def get_current_user() -> str:
    return getpass.getuser()


def get_current_user_slack_name() -> str:
    current_user: str = get_current_user()
    print(current_user)
    slack_name = SERVER_USERNAME_TO_SLACK_NAME.get(current_user)
    if slack_name is None:
        DIE(
            f"Could not find user {current_user} in the username to slack name mapping!"
        )
    return slack_name


def _get_current_server_hostname() -> str:
    return socket.gethostname()


def _hostname_to_enum(hostname: str) -> Server:
    match hostname:
        case "black":
            return Server.BLACK
        case "scholes":
            return Server.SCHOLES
        case _:
            return Server.FOREIGN
