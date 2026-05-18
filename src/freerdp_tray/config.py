import json
import os
import shlex
import socket
import subprocess
import threading
import traceback
from collections import OrderedDict
from typing import List, Dict, Any, Optional
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# known xfreerdp error codes:
# https://github.com/FreeRDP/FreeRDP/blob/f7dc5e0005afcdb7d6ef09c5e4daa40c5d5452dd/client/X11/xfreerdp.h#L338
# section 0 - 15: protocol - independent codes
XF_EXIT_SUCCESS = 0,
XF_EXIT_DISCONNECT = 1,
XF_EXIT_LOGOFF = 2,
XF_EXIT_IDLE_TIMEOUT = 3,
XF_EXIT_LOGON_TIMEOUT = 4,
XF_EXIT_CONN_REPLACED = 5,
XF_EXIT_OUT_OF_MEMORY = 6,
XF_EXIT_CONN_DENIED = 7,
XF_EXIT_CONN_DENIED_FIPS = 8,
XF_EXIT_USER_PRIVILEGES = 9,
XF_EXIT_FRESH_CREDENTIALS_REQUIRED = 10,
XF_EXIT_DISCONNECT_BY_USER = 11,

# section 16 - 31: license error set
XF_EXIT_LICENSE_INTERNAL = 16,
XF_EXIT_LICENSE_NO_LICENSE_SERVER = 17,
XF_EXIT_LICENSE_NO_LICENSE = 18,
XF_EXIT_LICENSE_BAD_CLIENT_MSG = 19,
XF_EXIT_LICENSE_HWID_DOESNT_MATCH = 20,
XF_EXIT_LICENSE_BAD_CLIENT = 21,
XF_EXIT_LICENSE_CANT_FINISH_PROTOCOL = 22,
XF_EXIT_LICENSE_CLIENT_ENDED_PROTOCOL = 23,
XF_EXIT_LICENSE_BAD_CLIENT_ENCRYPTION = 24,
XF_EXIT_LICENSE_CANT_UPGRADE = 25,
XF_EXIT_LICENSE_NO_REMOTE_CONNECTIONS = 26,

# section 128-254: xfreerdp specific exit codes
XF_EXIT_PARSE_ARGUMENTS = 128
XF_EXIT_MEMORY = 129
XF_EXIT_PROTOCOL = 130
XF_EXIT_CONN_FAILED = 131
XF_EXIT_AUTH_FAILURE = 132
XF_EXIT_NEGO_FAILURE = 133
XF_EXIT_LOGON_FAILURE = 134
XF_EXIT_ACCOUNT_LOCKED_OUT = 135
XF_EXIT_PRE_CONNECT_FAILED = 136
XF_EXIT_CONNECT_UNDEFINED = 137
XF_EXIT_POST_CONNECT_FAILED = 138
XF_EXIT_DNS_ERROR = 139
XF_EXIT_DNS_NAME_NOT_FOUND = 140
XF_EXIT_CONNECT_FAILED = 141
XF_EXIT_MCS_CONNECT_INITIAL_ERROR = 142
XF_EXIT_TLS_CONNECT_FAILED = 143
XF_EXIT_INSUFFICIENT_PRIVILEGES = 144
XF_EXIT_CONNECT_CANCELLED = 145
XF_EXIT_CONNECT_TRANSPORT_FAILED = 147
XF_EXIT_CONNECT_PASSWORD_EXPIRED = 148
XF_EXIT_CONNECT_PASSWORD_MUST_CHANGE = 149
XF_EXIT_CONNECT_KDC_UNREACHABLE = 150
XF_EXIT_CONNECT_ACCOUNT_DISABLED = 151
XF_EXIT_CONNECT_PASSWORD_CERTAINLY_EXPIRED = 152
XF_EXIT_CONNECT_CLIENT_REVOKED = 153
XF_EXIT_CONNECT_WRONG_PASSWORD = 154
XF_EXIT_CONNECT_ACCESS_DENIED = 155
XF_EXIT_CONNECT_ACCOUNT_RESTRICTION = 156
XF_EXIT_CONNECT_ACCOUNT_EXPIRED = 157
XF_EXIT_CONNECT_LOGON_TYPE_NOT_GRANTED = 158
XF_EXIT_CONNECT_NO_OR_MISSING_CREDENTIALS = 159
XF_EXIT_CONNECT_TARGET_BOOTING = 160

XF_EXIT_CODES = {
    XF_EXIT_SUCCESS: "Success",
    XF_EXIT_DISCONNECT: "Disconnect",
    XF_EXIT_LOGOFF: "Logoff",
    XF_EXIT_IDLE_TIMEOUT: "Idle timeout",
    XF_EXIT_LOGON_TIMEOUT: "Login timeout",
    XF_EXIT_CONN_REPLACED: "Connection replaced",
    XF_EXIT_OUT_OF_MEMORY: "Out of memory",
    XF_EXIT_CONN_DENIED: "Connection denied",
    XF_EXIT_CONN_DENIED_FIPS: "Connection denied FIPS",
    XF_EXIT_USER_PRIVILEGES: "User privileges",
    XF_EXIT_FRESH_CREDENTIALS_REQUIRED: "Fresh credentials required",
    XF_EXIT_DISCONNECT_BY_USER: "Disconnect by user",
    XF_EXIT_LICENSE_INTERNAL: "License: internal",
    XF_EXIT_LICENSE_NO_LICENSE_SERVER: "License: no license server",
    XF_EXIT_LICENSE_NO_LICENSE: "License: no license",
    XF_EXIT_LICENSE_BAD_CLIENT_MSG: "License: bad client message",
    XF_EXIT_LICENSE_HWID_DOESNT_MATCH: "License: hardware ID doesn't match",
    XF_EXIT_LICENSE_BAD_CLIENT: "License: bad client",
    XF_EXIT_LICENSE_CANT_FINISH_PROTOCOL: "License: can't finish protocol",
    XF_EXIT_LICENSE_CLIENT_ENDED_PROTOCOL: "License: client ended protocol",
    XF_EXIT_LICENSE_BAD_CLIENT_ENCRYPTION: "License: bad client encryption",
    XF_EXIT_LICENSE_CANT_UPGRADE: "License: can't upgrade",
    XF_EXIT_LICENSE_NO_REMOTE_CONNECTIONS: "License: no remote connections",
    XF_EXIT_PARSE_ARGUMENTS: "Parse arguments",
    XF_EXIT_MEMORY: "Memory",
    XF_EXIT_PROTOCOL: "Protocol",
    XF_EXIT_CONN_FAILED: "Connection failed",
    XF_EXIT_AUTH_FAILURE: "Authentication failure",
    XF_EXIT_NEGO_FAILURE: "Negotitation failure",
    XF_EXIT_LOGON_FAILURE: "Logon failure",
    XF_EXIT_ACCOUNT_LOCKED_OUT: "Account locked out",
    XF_EXIT_PRE_CONNECT_FAILED: "Pre-connect failed",
    XF_EXIT_CONNECT_UNDEFINED: "Connect undefined",
    XF_EXIT_POST_CONNECT_FAILED: "Post-connect failed",
    XF_EXIT_DNS_ERROR: "DNS error",
    XF_EXIT_DNS_NAME_NOT_FOUND: "DNS name not found",
    XF_EXIT_CONNECT_FAILED: "Connect: failed",
    XF_EXIT_MCS_CONNECT_INITIAL_ERROR: "MCS connect: initial error",
    XF_EXIT_TLS_CONNECT_FAILED: "TLS connect: failed",
    XF_EXIT_INSUFFICIENT_PRIVILEGES: "Insufficient privileges",
    XF_EXIT_CONNECT_CANCELLED: "Connect: cancelled",
    XF_EXIT_CONNECT_TRANSPORT_FAILED: "Connect: transport failed",
    XF_EXIT_CONNECT_PASSWORD_EXPIRED: "Connect: password expired",
    XF_EXIT_CONNECT_PASSWORD_MUST_CHANGE: "Connect: password must change",
    XF_EXIT_CONNECT_KDC_UNREACHABLE: "Connect: KDC unreachable",
    XF_EXIT_CONNECT_ACCOUNT_DISABLED: "Connect: account disabled",
    XF_EXIT_CONNECT_PASSWORD_CERTAINLY_EXPIRED: "Connect: password certainly expired",
    XF_EXIT_CONNECT_CLIENT_REVOKED: "Connect: client revoked",
    XF_EXIT_CONNECT_WRONG_PASSWORD: "Connect: wrong password",
    XF_EXIT_CONNECT_ACCESS_DENIED: "Connect: access denied",
    XF_EXIT_CONNECT_ACCOUNT_RESTRICTION: "Connect: account restriction",
    XF_EXIT_CONNECT_ACCOUNT_EXPIRED: "Connect: account expired",
    XF_EXIT_CONNECT_LOGON_TYPE_NOT_GRANTED: "Connect: logon type not granted",
    XF_EXIT_CONNECT_NO_OR_MISSING_CREDENTIALS: "Connect: no or missing credentials",
    XF_EXIT_CONNECT_TARGET_BOOTING: "Connect: target booting",
}


THEMES = OrderedDict({
    "Dark": "icon_dark.png",
    "Light": "icon_light.png",
})
APPLICATION_NAME = "freerdp-trayicon"


KEY_TERMINAL = "terminal"
KEY_PROMPT_PASSWORD = "promptPassword"
KEY_SSH_TUNNEL = "sshTunnel"
KEY_OPTIONS = "options"

XFREERDP = "xfreerdp"


def config_dir() -> str:
    """
    Returns the config directory ($HOME/.config/python-pulseaudio-profiles-trayicon).

    :return: the directory for the configurations
    :rtype: str
    """

    return os.path.expanduser("~/.config/" + APPLICATION_NAME)


def config_file() -> str:
    """
    Returns the config file ($HOME/.config/python-pulseaudio-profiles-trayicon/config.json).

    :return: the directory for the configurations
    :rtype: str
    """

    return os.path.join(config_dir(), "config.json")


def init_config_dir() -> bool:
    """
    Ensures that the config directory is present.

    :return: if directory present
    :rtype: bool
    """

    d = config_dir()
    if os.path.exists(d):
        return os.path.isdir(d)
    else:
        os.mkdir(d, mode=0o700)
        return True


def default_settings() -> Dict:
    """
    Returns the default settings.

    :return: the default settings
    :rtype: dict
    """
    return {
        "theme": "Dark",
    }


def load_config() -> Dict:
    """
    Loads the configuration from disk.

    :return: the configuration
    :rtype: dict
    """
    if not os.path.exists(config_dir()):
        init_config_dir()

    # load config from disk
    fname = config_file()
    if not os.path.exists(fname):
        result = dict()
    else:
        with open(fname, "r") as cf:
            result = json.load(cf)

    # fill in missing default values
    default = default_settings()
    for k in default:
        if k not in result:
            result[k] = default[k]

    return result


def connection_path(connection: str) -> str:
    """
    Assembles the full path for a connection.

    :param connection: the name of the connection
    :type connection: str
    :return: the full path
    :rtype: str
    """
    return os.path.join(config_dir(), connection + ".jrdp")


def list_connections() -> List[str]:
    """
    Lists the available connections.

    :return: the list of connection names
    :rtype: list
    """
    result = []

    if not os.path.exists(config_dir()):
        init_config_dir()

    for f in os.listdir(config_dir()):
        if f.endswith(".jrdp"):
            result.append(os.path.splitext(f)[0])

    result.sort()

    return result


def remove_connection(connection: str) -> bool:
    """
    Deletes the specified connection.

    :param connection: the name of the connection to delete
    :type connection: str
    :return: whether successful
    :rtype: bool
    """
    if not os.path.exists(config_dir()):
        init_config_dir()

    f = connection_path(connection)
    if os.path.exists(f):
        print("Deleting: %s" % f)
        try:
            os.remove(f)
            return True
        except:
            print("Failed to delete: %s" % f)
            traceback.print_exc()
    return False


def load_connection(connection: str) -> Optional[Dict[str, Any]]:
    """
    Loads the specified connection and returns the configuration dictionary.

    :param connection: the name of the connection to load
    :type connection: str
    :return: the connection information or None if failed to load
    :rtype: dict or None
    """
    if not os.path.exists(config_dir()):
        init_config_dir()

    f = connection_path(connection)
    if not os.path.exists(f):
        return None

    with open(f, "r") as fp:
        return json.load(fp)


def save_connection(connection: str, options: Dict[str, Any]) -> bool:
    """
    Saves the options under the specified connection name.

    :param connection: the name of the connection
    :type connection: str
    :param options: the parameters for the connection
    :type options: dict
    :return: whether successfully saved
    :rtype: bool
    """
    if not os.path.exists(config_dir()):
        init_config_dir()

    f = connection_path(connection)
    try:
        print("Saving connection '%s' to: %s" % (connection, f))
        with open(f, "w") as fp:
            json.dump(options, fp, indent=2)
            return True
    except:
        print("Failed to save connection '%s' to: %s" % (connection, f))
        traceback.print_exc()

    return False


def get_next_port() -> Optional[int]:
    """
    Determines a free port to use for ssh tunneling.

    Taken from here:
    https://superuser.com/a/1671326

    :return: the port, None if failed to determine
    :rtype: int
    """
    try:
        s = socket.socket()
        s.bind(('', 0))
        result = s.getsockname()[1]
        s.close()
        return result
    except:
        print("Failed to determine free port!")
        traceback.print_exc()
        return None


def extract_host(options: str) -> Optional[str]:
    """
    Extracts the host from the freerdp options.

    :param options: the options to parse
    :type options: str
    :return: the host, None if not found
    :rtype: str
    """
    parts = shlex.split(options)
    for part in parts:
        if part.startswith("/v:"):
            return part[3:]

    print("Failed to extract host from: %s" % options)
    return None


def replace_host(options: str, new_host: str) -> str:
    """
    Replaces the host (/v:...) in the freerdp options with the new one.

    :param options: the options to update
    :type options: str
    :param new_host: the new host to use (incl port)
    :type new_host: str
    :return: the updated options
    :rtype: str
    """
    parts = shlex.split(options)
    for i, part in enumerate(parts):
        if part.startswith("/v:"):
            parts[i] = "/v:" + new_host
            return shlex.join(parts)

    print("Failed to replace host in: %s" % options)
    return options


def open_connection(connection: str, params: Dict[str, Any], password: str = None):
    """
    Builds the command using the specified parameters and performs a remote connect.

    :param connection: the name of the connection
    :type connection: str
    :param params: the parameters for the connection
    :type params: dict
    :param password: the password to use, ignored if None
    :type password: str
    """
    print("Connecting: %s" % connection)

    options = params[KEY_OPTIONS]
    if password is not None:
        options += ' "/p:%s"' % password

    tunnel = None
    if KEY_SSH_TUNNEL in params:
        port = get_next_port()
        if port is None:
            print("No port determine, cannot launch ssh tunnel!")
            return
        host = extract_host(options)
        options = replace_host(options, "localhost:%d" % port)
        tunnel = "ssh -f -L " + str(port) + ":localhost:3389 " + host + " sleep 1"

    # TODO in terminal?

    # launch
    cmd = XFREERDP + " " + options
    if tunnel is not None:
        cmd = "bash -c '" + tunnel + "; " + cmd + "'"
    thread = threading.Thread(target=run_command, args=(cmd,))
    thread.start()


def mask_password(cmd: str) -> str:
    """
    Masks the password in the command.

    :param cmd: the command to process
    :type cmd: str
    :return: the updated command
    :rtype: str
    """
    result = cmd
    if "/p:" in cmd:
        mask = [False] * len(cmd)
        for i in range(cmd.index("/p:")+3, len(cmd)):
            s = cmd[i:i+1]
            if s == " ":
                break
            mask[i] = True
        result = ""
        for i in range(len(cmd)):
            if mask[i]:
                result += "*"
            else:
                result += cmd[i:i+1]
    return result


def run_command(cmd: str):
    """
    Executes the specified command.

    :param cmd: the command to execute
    :type cmd: str
    """
    try:
        args = shlex.split(cmd)
        res = subprocess.run(args)
        print("Exit code: %d", res.returncode)

        # exit codes
        # https://github.com/FreeRDP/FreeRDP/blob/f7dc5e0005afcdb7d6ef09c5e4daa40c5d5452dd/client/X11/xfreerdp.h#L338
        show_error_msg = res.returncode != 0
        if res.returncode == 1:  # XF_EXIT_SUCCESS
            show_error_msg = False
        elif res.returncode == 2:  # XF_EXIT_LOGOFF
            show_error_msg = False
        elif res.returncode == 11:  # XF_EXIT_DISCONNECT_BY_USER
            show_error_msg = False
        elif res.returncode == 12:  # ??? Windows sign out ???
            show_error_msg = False

        if show_error_msg:
            if res.returncode in XF_EXIT_CODES:
                msg = "exit code %d: %s" % (res.returncode, XF_EXIT_CODES[res.returncode])
            else:
                msg = "exit code %d" % res.returncode
            dialog = Gtk.MessageDialog(
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Failed to run command (%s):\n%s" % (msg, mask_password(cmd)),
            )
            dialog.run()
            dialog.destroy()
    except:
        print("Failed to execute: %s" % mask_password(cmd))
        traceback.print_exc()
