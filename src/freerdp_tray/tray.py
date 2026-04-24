import os
import json
import traceback
import gi
from freerdp_tray.config import THEMES, config_file, load_config, list_connections, remove_connection, \
    load_connection, save_connection, open_connection, KEY_OPTIONS, KEY_TERMINAL, KEY_PROMPT_PASSWORD, KEY_SSH_TUNNEL, \
    XFREERDP
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3, GLib, GObject

CURRPATH = os.path.dirname(os.path.realpath(__file__))
""" for locating the icon for the indicator. """

indicator = None
""" the tray icon indicator instance. """

""" the name of the application. """


class ConfirmationDialog(Gtk.Dialog):
    """
    Simple confirmation dialog. Based on code from here:
    https://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html#messagedialog
    """

    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(
            self,
            "Confirmation",
            parent,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )

        self.set_default_size(150, 100)
        label = Gtk.Label(label=msg)
        box = self.get_content_area()
        box.add(label)
        self.show_all()


class InputDialog(Gtk.Dialog):
    """
    Simple input dialog. Based on code from here:
    https://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html#messagedialog
    """

    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(
            self,
            "Input",
            parent,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )

        self.set_default_size(150, 100)
        label = Gtk.Label(label=msg)
        box = self.get_content_area()
        box.add(label)
        self.entry = Gtk.Entry()
        box.add(self.entry)
        self.show_all()


class PasswordDialog(Gtk.Dialog):
    """
    Simple password dialog. Based on code from here:
    """

    def __init__(self, parent, msg):
        Gtk.Dialog.__init__(
            self,
            "Password",
            parent,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )

        self.set_default_size(150, 100)
        label = Gtk.Label(label=msg)
        box = self.get_content_area()
        box.add(label)
        self.entry = Gtk.Entry()
        self.entry.set_visibility(False)
        box.add(self.entry)
        self.show_all()


def current_theme():
    """
    Returns the currently configured theme.

    :return: the current theme
    :rtype: str
    """
    result = "Dark"
    config = load_config()
    if ("theme" in config) and (config["theme"] in THEMES):
        result = config["theme"]
    return result


def store_theme(theme):
    """
    Stores the theme as the default one.

    :param theme: the theme to use
    :type theme: str
    """
    print("Applying theme: %s" % theme)
    config = load_config()
    config["theme"] = theme
    with open(config_file(), "w") as cf:
        json.dump(config, cf, indent=2)


def main():
    """
    The main method for starting up the tray icon
    """

    global indicator
    indicator = AppIndicator3.Indicator.new(
        "customtray",
        CURRPATH + "/" + THEMES[current_theme()],
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu())
    Gtk.main()


def menu():
    """
    Generates the menu and returns it.

    :return: the menu
    :rtype: Gtk.Menu
    """

    result = Gtk.Menu()

    connections = list_connections()

    # create
    menuitem_create = Gtk.MenuItem(label='Create...')
    menuitem_create.connect('activate', create_connection)
    result.append(menuitem_create)

    # launch
    if len(connections) > 0:
        menu_connect = Gtk.Menu()
        menuitem_connect = Gtk.MenuItem(label='Connect')
        menuitem_connect.set_submenu(menu_connect)
        result.append(menuitem_connect)
        for profile in connections:
            menuitem = Gtk.MenuItem(label=profile)
            menuitem.connect('activate', launch_connection)
            menu_connect.append(menuitem)
    else:
        menuitem_connect = Gtk.MenuItem(label='Connect')
        menuitem_connect.set_sensitive(False)
        result.append(menuitem_connect)

    # delete
    if len(connections) > 0:
        menu_delete = Gtk.Menu()
        menuitem_delete = Gtk.MenuItem(label='Delete')
        menuitem_delete.set_submenu(menu_delete)
        result.append(menuitem_delete)
        for profile in connections:
            menuitem = Gtk.MenuItem(label=profile)
            menuitem.connect('activate', delete_connection)
            menu_delete.append(menuitem)
    else:
        menuitem_delete = Gtk.MenuItem(label='Delete')
        menuitem_delete.set_sensitive(False)
        result.append(menuitem_delete)

    result.append(Gtk.SeparatorMenuItem())

    # refresh
    menuitem_refresh = Gtk.MenuItem(label='Refresh')
    menuitem_refresh.connect('activate', refresh_connections)
    result.append(menuitem_refresh)

    result.append(Gtk.SeparatorMenuItem())

    # themes
    menu_theme = Gtk.Menu()
    menuitem_theme = Gtk.MenuItem(label='Theme')
    menuitem_theme.set_submenu(menu_theme)
    result.append(menuitem_theme)
    for k in THEMES:
        menuitem = Gtk.MenuItem(label=k)
        menuitem.connect('activate', select_theme)
        menu_theme.append(menuitem)

    result.append(Gtk.SeparatorMenuItem())

    # exit
    menuitem_exit = Gtk.MenuItem(label='Exit')
    menuitem_exit.connect('activate', exit_tray)
    result.append(menuitem_exit)

    result.show_all()
    return result


def update_menu():
    """
    Updates the menu.
    """

    global indicator
    indicator.set_menu(menu())


def create_connection(_):
    """
    Creates a new connection, prompting the user for parameters.
    """

    # connection name
    dialog = InputDialog(None, "Please enter connection name:")
    response = dialog.run()
    if response != Gtk.ResponseType.OK:
        dialog.destroy()
        return
    connection = dialog.entry.get_text()
    dialog.destroy()

    # options
    dialog = InputDialog(None, "Please enter %s options:" % XFREERDP)
    response = dialog.run()
    if response != Gtk.ResponseType.OK:
        dialog.destroy()
        return
    options = dialog.entry.get_text()
    dialog.destroy()

    # prompt for password?
    dialog = InputDialog(None, "Prompt for password (y/n)?")
    response = dialog.run()
    if response != Gtk.ResponseType.OK:
        dialog.destroy()
        return
    prompt_password = dialog.entry.get_text().lower() == "y"
    dialog.destroy()

    # ssh tunnel?
    dialog = InputDialog(None, "Use SSH tunnel (y/n)?")
    response = dialog.run()
    if response != Gtk.ResponseType.OK:
        dialog.destroy()
        return
    ssh_tunnel = dialog.entry.get_text().lower() == "y"
    dialog.destroy()

    # in terminal?
    # TODO enable
    in_terminal = False
    # dialog = InputDialog(None, "Run in terminal (y/n)?")
    # response = dialog.run()
    # if response != Gtk.ResponseType.OK:
    #     dialog.destroy()
    #     return
    # in_terminal = dialog.entry.get_text().lower() == "y"
    # dialog.destroy()

    print("Creating connection: %s" % connection)
    params = {
        KEY_OPTIONS: options,
        KEY_TERMINAL: in_terminal,
        KEY_PROMPT_PASSWORD: prompt_password,
        KEY_SSH_TUNNEL: ssh_tunnel
    }
    ok = save_connection(connection, params)
    if not ok:
        dialog = Gtk.MessageDialog(
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Failed to save connection: %s" % connection,
        )
        dialog.run()
        dialog.destroy()
    update_menu()


def launch_connection(e):
    """
    Launches the connection with the name stored in the label.

    :param e: the menu item that triggered the event
    :type e: Gtk.MenuItem
    """

    connection = e.get_label()
    print("Loading: %s" % connection)
    params = load_connection(connection)
    if params is None:
        print("Failed to load connection data for: %s" % connection)

    # password prompt?
    password = None
    if (KEY_PROMPT_PASSWORD in params) and params[KEY_PROMPT_PASSWORD]:
        dialog = PasswordDialog(None, "Please enter password:")
        response = dialog.run()
        if response != Gtk.ResponseType.OK:
            dialog.destroy()
            return
        password = dialog.entry.get_text()
        dialog.destroy()

    open_connection(connection, params, password=password)


def delete_connection(e):
    """
    Deletes the connection with the name stored in the label.

    :param e: the menu item that triggered the event
    :type e: Gtk.MenuItem
    """

    connection = e.get_label()

    dialog = ConfirmationDialog(None, "Do you want to delete connection '%s'?" % connection)
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        print("Deleting connection: %s" % connection)
        remove_connection(connection)
        update_menu()

    dialog.destroy()


def refresh_connections(_):
    """
    Re-creates the menu.
    """

    print("Refreshing connections")
    update_menu()


def select_theme(e):
    """
    Applies the theme with the name stored in the label.

    :param e: the menu item that triggered the event
    :type e: Gtk.MenuItem
    """
    global indicator
    theme = e.get_label()
    store_theme(theme)
    icon = THEMES[theme]
    indicator.set_icon(CURRPATH + "/" + icon)


def exit_tray(_):
    """
    Exits the tray icon menu.
    """

    Gtk.main_quit()


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
