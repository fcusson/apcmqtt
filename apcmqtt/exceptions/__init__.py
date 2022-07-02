"""Exceptions specifically for the apcmqtt module

Exceptions:
    DependencyError: A Dependency is missing
    ApcAccessConnectionError: Unable to connect to the apcupsd instance
    MqttConnectionError: Unable to connect to the mqtt broker
    ConfigurationError: A key configuration is missing
    MissingConfigError: The configuration file could not be located in
        the specified location
"""


class DependencyError(Exception):
    """A Dependency is missing"""


class ApcAccessConnectionError(Exception):
    """Unable to connect to the apcupsd instance"""


class MqttConnectionError(Exception):
    """Unable to connect to the mqtt broker"""


class ConfigurationError(Exception):
    """A key configuration is missing"""


class MissingConfigError(Exception):
    """The configuration file could not be located in the specified
    location"""
