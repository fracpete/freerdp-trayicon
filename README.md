# freerdp-trayicon
Python library that adds a tray icon for easily launching [freerdp](https://github.com/FreeRDP/FreeRDP) connections.

You can start the tray icon with `freerdp-tray`.

## Installation

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
