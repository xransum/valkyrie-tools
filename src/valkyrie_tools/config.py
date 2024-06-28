"""Config module."""

import configparser
import os
from typing import Any, Dict

from appdirs import user_config_dir


class Config:
    """A class for managing a configuration file in the user's config directory.

    Attributes:
        config_name (str): The name of the configuration file.
        config_file (str): The full path to the configuration file.
        config (configparser.ConfigParser): The configparser for the
            configuration file.
    """

    def __init__(
        self,
        config_name: str,
        defaults: Dict[str, Dict[str, Any]] = None,
    ):
        """Initialize the Config object.

        Args:
            config_name (str): The name of the configuration file.
            defaults (dict, optional): The configuration default values.
                Defaults to None.
        """
        self.config_name = config_name
        self.config_file = os.path.join(user_config_dir(), f".{config_name}")
        self.config = configparser.ConfigParser()
        self.defaults = defaults

        if self.read() == [] and self.defaults is not None:
            self.set_defaults()

    def read(self):
        """Load the configuration file."""
        return self.config.read(self.config_file)

    def save(self):
        """Save the configuration file."""
        with open(self.config_file, "w") as f:
            self.config.write(f)

    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """Get the value of an option in a section.

        Args:
            section (str): The section of the option.
            option (str): The name of the option.
            fallback (Any): The fallback value if the option is not found.
                Defaults to None.

        Returns:
            Any: The value of the option.
        """
        return self.config.get(section, option, fallback=fallback)

    def set(self, section: str, option: str, value: Any):
        """Set the value of an option in a section.

        Args:
            section (str): The section of the option.
            option (str): The name of the option.
            value (Any): The value of the option.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, option, str(value))
        self.save()

    def remove_section(self, section: str):
        """Remove a section from the configuration file.

        Args:
            section (str): The section to remove.
        """
        self.config.remove_section(section)
        self.save()

    def remove_option(self, section: str, option: str):
        """Remove an option from a section.

        Args:
            section (str): The section of the option.
            option (str): The name of the option.
        """
        self.config.remove_option(section, option)
        self.save()

    def set_defaults(self):
        """Set default values for the configuration."""
        for section, options in self.defaults.items():
            for option, value in options.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                self.config.set(section, option, str(value))
        self.save()
