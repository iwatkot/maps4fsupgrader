"""Configuration for Maps4FS upgrader containers."""

import os

USERPROFILE = os.getenv("USERPROFILE")
if not USERPROFILE:
    raise EnvironmentError("USERPROFILE environment variable is not set.")


# pylint: disable=too-few-public-methods
class ContainerParams:
    """Container parameters."""

    maps4fsapi = {
        "image": "iwatkot/maps4fsapi",
        "name": "maps4fsapi",
        "ports": {"8000": "8000"},
        "volumes": {
            f"{USERPROFILE}/maps4fs/mfsrootdir": "/usr/src/app/mfsrootdir",
            f"{USERPROFILE}/maps4fs/templates": "/usr/src/app/templates",
            f"{USERPROFILE}/maps4fs/defaults": "/usr/src/app/defaults",
            "/var/run/docker.sock": "/var/run/docker.sock",
        },
        "restart_policy": {"Name": "unless-stopped"},
        "pull_policy": "always",
    }

    maps4fsui = {
        "image": "iwatkot/maps4fsui",
        "name": "maps4fsui",
        "ports": {"3000": "3000"},
        "volumes": {
            f"{USERPROFILE}/maps4fs/mfsrootdir": "/usr/src/app/mfsrootdir",
            f"{USERPROFILE}/maps4fs/templates": "/usr/src/app/templates",
            f"{USERPROFILE}/maps4fs/defaults": "/usr/src/app/defaults",
            "/var/run/docker.sock": "/var/run/docker.sock",
        },
        "restart_policy": {"Name": "unless-stopped"},
        "pull_policy": "always",
    }
