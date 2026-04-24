# freerdp-trayicon
Python library that adds a tray icon for easily launching [freerdp](https://github.com/FreeRDP/FreeRDP) 
connections via `xfreerdp`.

You can start the tray icon with `freerdp-tray`.

## Installation

### Install xfreerdp

If not already present on your system:

```bash
sudo apt install freerdp2-x11
```

### Prerequisites

Make sure you have the following dependencies installed:

```bash
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1
```

### pip

Create a virtual environment and activate it:

```bash
python3 -m venv --system-site-packages freerdp-trayicon
. ./freerdp-trayicon/bin/activate
```

You can install the tool as follows:

```bash
pip install freerdp-trayicon
```

Or straight from the repository:

```bash
pip install git+https://github.com/fracpete/freerdp-trayicon.git
```


### Debian

Or, when running Debian/Ubuntu, download and install the Debian package from the 
[Releases section](https://github.com/fracpete/freerdp-trayicon/releases).


## Config files

**NB:** The user gets directed through prompts when selecting *Create...*
from the tray-icon menu. You don't have to create these files yourself.

The config files of the connections get stored in the following location:

```bash
$HOME/.config/freerdp-trayicon
```

The file format is JSON and supports the following parameters:

```
{
  "options": "XFREERDP OPTIONS", 
  "promptPassword": BOOLEAN,
  "sshTunnel": BOOL
}
```

* `options`: the options for xfreerdp
* `promptPassword`: whether to prompt the user for a password and add it to the options as `/p:PASSWORD`
* `sshTunnel`: whether to connect through a local ssh tunnel

Examples:

* connect as user `USER` to remote host `HOST` via the gateway `GATEWAY`, 
  get prompted for a password but don't use an ssh tunnel:

```json
{
  "options": "/u:USER /w:1280 /h:960 /v:HOST /g:GATEWAY",
  "promptPassword": true,
  "sshTunnel": false
}
```

* connect to remote host `HOST` using an ssh tunnel:

```json
{
  "options": "/w:1280 /h:960 /v:HOST",
  "promptPassword": false,
  "sshTunnel": true
}
```
