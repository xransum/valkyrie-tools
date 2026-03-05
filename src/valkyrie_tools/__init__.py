"""Valkyrie Tools.

A collection of command-line network analysis utilities covering URL, IP
address, DNS, and WHOIS inspection.  The package exposes a single pre-built
:class:`~valkyrie_tools.config.Config` instance (:data:`configs`) that every
sub-command shares for persistent configuration.
"""

__all__ = ["__version__", "DEFAULT_CONFIG_FILE", "config"]

__appname__ = "valkyrie_tools"
__version__ = "0.1.0"  # noqa

# from .configs import Config

# DEFAULT_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".valkyrie")
# config = Config(DEFAULT_CONFIG_FILE)


# CONFIG_DIR = user_config_dir(__appname__)
# CONFIG_FILE = os.path.join(CONFIG_DIR, f"{__appname__}")


from .config import Config


configs = Config(
    __appname__,
    defaults={
        "GLOBAL": {"virusTotalApiKey": ""},
    },
)
"""Package-level :class:`~valkyrie_tools.config.Config` singleton.

Stores user configuration for all ``valkyrie-tools`` commands in an INI-format
file located in the platform-appropriate user config directory (resolved via
``appdirs.user_config_dir``).  The file is created automatically with default
values on first run when it does not yet exist.
"""
