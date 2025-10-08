"""Configuration for Maps4FS upgrader containers."""


# pylint: disable=too-few-public-methods
class ContainerParams:
    """Container parameters."""

    maps4fsapi = {
        "image": "iwatkot/maps4fsapi",
        "name": "maps4fsapi",
        "ports": {"8000": "8000"},
        "volumes": {
            "${USERPROFILE}/maps4fs/mfsrootdir": "/usr/src/app/mfsrootdir",
            "${USERPROFILE}/maps4fs/templates": "/usr/src/app/templates",
            "${USERPROFILE}/maps4fs/defaults": "/usr/src/app/defaults",
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
            "${USERPROFILE}/maps4fs/mfsrootdir": "/usr/src/app/mfsrootdir",
            "${USERPROFILE}/maps4fs/templates": "/usr/src/app/templates",
            "${USERPROFILE}/maps4fs/defaults": "/usr/src/app/defaults",
            "/var/run/docker.sock": "/var/run/docker.sock",
        },
        "restart_policy": {"Name": "unless-stopped"},
        "pull_policy": "always",
        "depends_on": ["maps4fsapi"],
    }
