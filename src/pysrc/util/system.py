import getpass
import logging
import socket

from pysrc.util.exceptions import DIE
from pysrc.util.types import Server

_logger = logging.getLogger(__name__)

SERVER_USERNAME_TO_SLACK_NAME: dict[str, str] = {
    "echavemann": "Ethan Havemann",
    "ahuang9999": "Alex Huang",
    "andrlime": "Andrew Li",
    "avillasenor": "Aidan Villasenor",
    "bhu": "Blake Hu",
    "chengian": "Ian Cheng",
    "dsl": "Daniel Lee",
    "efang": "Eddie Fang",
    "franklin": "Franklin Zhao",
    "fzhang": "Frank Zhang",
    "gwang": "Gavin Wang",
    "hguan": "Harry Guan",
    "jasonzhxn": "Jason Zhan",
    "jay": "Jay Park",
    "JCJR": "Jerry Cao",
    "jenny": "Jenny Zhou",
    "jerry": "Jerry Han",
    "john": "John Hileman",
    "maxbreslin": "Max Breslin",
    "mglass": "Max Glass",
    "minnce": "Chris Minn",
    "miya": "Miya Liu",
    "mmaiti": "Milind Maiti",
    "mossbarger": "Luke Mossbarger",
    "myang": "Kevin Y",
    "nikola": "Nino",
    "nolenca": "Clayton Nolen",
    "nwangjs": "Nathan Wang",
    "rewong": "Ryan Wong",
    "rmohan": "Romir Mohan",
    "steev": "Steve Ewald",
    "wbrittian": "Will Brittian",
    "wu": "Nathan Wu",
    "xyliu": "Yang Liu",
}


def get_current_server() -> Server:
    hostname = _get_current_server_hostname()
    return _hostname_to_enum(hostname)


def get_current_user() -> str:
    return getpass.getuser()


def get_current_user_slack_name() -> str:
    current_user: str = get_current_user()
    logging.debug(f"Current user: {current_user}")
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
