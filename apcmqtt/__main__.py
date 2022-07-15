#!/usr/bin/python
"""apcmqtt - apcupsd to mqtt translation layer

This modules monitors apcupsd continuously and updates an MQTT on the
changes of status

functions:
    main(): code entrypoint
"""

__version__ = "1.0.0"
__author__ = "Felix Cusson"

from time import sleep
import argparse
import logging

import yaml

from apcmqtt.apc import Ups
from apcmqtt.mqtt import Publisher
from apcmqtt.exceptions import (
    MissingConfigError,
    ConfigurationError,
    ApcAccessConnectionError,
    MqttConnectionError,
)
import apcmqtt.utils as utils

LOGGER = logging.getLogger(__name__)


def setup(config_file: str) -> tuple[dict[str, Ups], Publisher, int]:
    """general setup before starting the main loop of the script"""

    # get the config information
    try:
        utils.log_message(
            LOGGER,
            f"Reading config file located at {config_file}",
            logging.DEBUG
        )
        with open(config_file, mode='r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as exc:
        raise MissingConfigError("Config file not found") from exc

    # get the config for the mqtt broker
    try:
        utils.log_message(
            LOGGER,
            "populating variables from config dictionnary",
            logging.DEBUG
        )
        ups_dict = find_ups(config["ups"])
        user = config["mqtt"]["user"]
        password = config["mqtt"]["password"]
        host = config["mqtt"]["host"]
        port = config["mqtt"]["port"]
        root_topic = config["mqtt"]["root_topic"]
        delay = config["script"]["delay"]
    except KeyError as exc:
        raise ConfigurationError(
            "Missing configuration element",
            str(exc),
        ) from exc

    utils.log_message(
        LOGGER,
        "Config file loaded",
        logging.INFO,
    )

    # create the mqtt_publisher instance
    utils.log_message(
        LOGGER,
        f"opening connexion with mqtt broker at {host}:{port} with user {user}",
        logging.DEBUG,
    )
    publisher = Publisher(user, password, host, port, root_topic)

    utils.log_message(
        LOGGER,
        "connexion to mqtt broker established",
        logging.INFO,
    )

    return ups_dict, publisher, delay


def loop(ups_list: dict[str, Ups], publisher: Publisher, delay: int) -> None:
    """main loop of the module that repeats until closed

    Args:
        ups_list (dict[str, Ups]): list of the different ups followed by
            the module
        publisher (Publisher): the mqtt publisher object
        delay (int): the delay in seconds between publishing
    """
    while True:
        utils.log_message(
            LOGGER,
            f"publishing information for {ups_list} on {publisher}",
            logging.DEBUG,
        )
        request_publishing(ups_list, publisher)
        utils.log_message(
            LOGGER,
            f"waiting delay of {delay}",
            logging.DEBUG,
        )
        sleep(delay)


def request_publishing(ups_list: dict[str, Ups], publisher: Publisher) -> None:
    """makes a request to the mqtt publisher

    Args:
        ups_list (dict[str, Ups]): list of ups to publish about
        publisher (Publisher): the mqtt publisher
    """
    for name, ups in ups_list.items():
        utils.log_message(
            LOGGER,
            f"Publishing data for {name} @{publisher.host}:{publisher.port}",
            logging.INFO,
        )

        try:
            utils.log_message(
                LOGGER,
                f"updating {name}'s information",
                logging.DEBUG,
            )
            ups.update()
            utils.log_message(
                LOGGER,
                f"publishing {name}'s information on {publisher}"
            )
            publisher.publish_ups_data(name, ups.get_dict())
        except (
            ApcAccessConnectionError,
            MqttConnectionError
        ):
            utils.log_message(
                LOGGER,
                "Unable to connect to mqtt broker",
                logging.WARNING,
            )


def gracefull_exit() -> None:
    """gracefully close the module"""
    utils.log_message(
        LOGGER,
        "Closing apcmqtt",
        logging.INFO,
    )
    exit(0)


def find_ups(ups_list: dict) -> dict[str, Ups]:
    """finds the ups listed in the config files

    Args:
        ups_list (dict): dictionary containing the ups's informations

    Returns:
        dict[str, Ups]: a dictionary with the name of the ups as key and
            the ups itself as value
    """
    ups_dict = {}

    utils.log_message(
        LOGGER,
        "finding list of ups in config file",
        logging.DEBUG,
    )
    for name, ups_config in ups_list.items():
        try:

            # get the config for the ups
            is_local = ups_config["is_local"]
            host = None
            port = None

            # if the ups is not local, make sure the host and port are
            # provided
            if not is_local:
                host, port = get_host_config(ups_config)

            ups = Ups(name, is_local, host, port)

            ups_dict[ups.name] = ups
        except KeyError as exc:
            raise exc

    return ups_dict


def get_host_config(ups: dict) -> tuple[str]:
    """returns the host and port config of a ups

    Args:
        ups (dict): list of parameters linked to a ups

    Raises:
        ConfigurationError: missing key configuration element in the
            config file

    Returns:
        tuple[str]: a tuple of the host and the port (in that order)
    """
    try:
        host = ups["host"]
        port = ups["port"]
    except KeyError as exc:
        raise ConfigurationError(
            "Missing configuration element", str(exc)
        ) from exc

    return (host, port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "A monitoring tool for apcups that sends data over MQTT messages to"
            " a broker at a regular interval"
        )
    )

    parser.add_argument(
        "-v",
        "--debug",
        help="sets the script to debug mode",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="location of the config file",
        default="/etc/apcmqtt/apcmqtt.yaml",
    )

    args = vars(parser.parse_args())

    if args["debug"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    config_location = args["config"]

    try:
        utils.log_message(
            LOGGER,
            "starting setup",
            logging.DEBUG,
        )
        UPS_DICT, PUBLISHER, DELAY = setup(config_location)
    except MissingConfigError:
        utils.log_message(
            LOGGER,
            f"Configuration file could not be found at {config_location}",
            logging.ERROR
        )
    except ConfigurationError as configExc:
        utils.log_message(
            LOGGER,
            f"Missing Configuration Key - {str(configExc)}",
            logging.ERROR
        )

    utils.log_message(LOGGER, "debug message test", logging.DEBUG)

    try:
        utils.log_message(
            LOGGER,
            "Starting main loop",
            logging.DEBUG
        )
        loop(UPS_DICT, PUBLISHER, DELAY)
    except KeyboardInterrupt:
        utils.log_message(
            LOGGER,
            "Received keyboard interupt",
            logging.DEBUG,
        )
        gracefull_exit()
