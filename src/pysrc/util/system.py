import socket
import getpass
from pysrc.util.types import Server

def get_current_server() -> Server:
    hostname = _get_current_server_hostname()
    return _hostname_to_enum(hostname)

def get_current_user() -> str:
    return getpass.getuser()

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
