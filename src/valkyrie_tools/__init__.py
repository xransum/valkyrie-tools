"""Valkyrie Tools."""

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
