import json
import os
import traceback
from collections import OrderedDict
from typing import List, Dict, Any, Optional


THEMES = OrderedDict({
    "Dark": "icon_dark.png",
    "Light": "icon_light.png",
})
APPLICATION_NAME = "freerdp-trayicon"


KEY_TERMINAL = "terminal"
KEY_PROMPT_PASSWORD = "promptPassword"
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
