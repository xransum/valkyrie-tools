"""Configuration management for valkyrie-tools.

Wraps :class:`configparser.ConfigParser` with a thin :class:`Config` class
that automatically locates the per-user configuration file (using
``appdirs.user_config_dir``), creates the file with sensible defaults on first
run, and exposes a simple ``get`` / ``set`` / ``remove`` API.  The file is
stored in INI format.
"""

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
        """Load the configuration file from disk.

        Reads :attr:`config_file` via :class:`configparser.ConfigParser`.
        If the file does not exist, ``configparser`` silently skips it and
        returns an empty list.

        Returns:
            List[str]: Paths of files successfully read (an empty list when
            the file does not exist yet).
        """
        return self.config.read(self.config_file)

    def save(self):
        """Write the current in-memory configuration to disk.

        Serialises :attr:`config` to :attr:`config_file` using
        :class:`configparser.ConfigParser`.  The file is created if it does
        not exist; intermediate directories must already exist.
        """
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
        """Apply :attr:`defaults` to the in-memory configuration and save.

        Iterates over all ``section -> {option: value}`` pairs in
        :attr:`defaults`, creates any missing sections, sets each option,
        then calls :meth:`save` once to persist the full configuration.
        Called automatically by :meth:`__init__` when ``defaults`` is
        provided and no configuration file was found on disk.
        """
        for section, options in self.defaults.items():
            for option, value in options.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                self.config.set(section, option, str(value))
        self.save()
