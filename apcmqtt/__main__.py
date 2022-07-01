"""apcmqtt - apcupsd to mqtt translation layer

This modules monitors apcupsd continuously and updates an MQTT on the
changes of status

functions:
    main(): code entrypoint
"""

__version__ = "0.1.2"
__author__ = "Felix Cusson"

from email import parser
from time import sleep
import argparse
import logging

import yaml

from apcmqtt.apc import Ups
from apcmqtt.mqtt import Publisher
from apcmqtt.exceptions import MissingConfigError, ConfigurationError
import apcmqtt.utils as utils

LOGGER = logging.getLogger(__name__)


def setup(config_file: str) -> tuple[dict[str, Ups], Publisher, int]:
    """general setup before starting the main loop of the script"""

    # get the config information
    try:
        with open(config_file, mode='r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as exc:
        raise MissingConfigError("Config file not found") from exc

    ups_dict = find_ups(config["ups"])
    # get the config for the mqtt broker
    try:
        user = config["mqtt"]["user"]
        password = config["mqtt"]["password"]
        host = config["mqtt"]["host"]
        port = config["mqtt"]["port"]
    except KeyError as exc:
        raise ConfigurationError(
            "Missing configuration element",
            str(exc),
        ) from exc

    # create the mqtt_publisher instance
    publisher = Publisher(user, password, host, port)
    #publisher.publish_ups_data(ups.name, ups.get_dict())

    delay = config["script"]["delay"]

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
        request_publishing(ups_list, publisher)
        sleep(delay)


def request_publishing(ups_list: dict[str, Ups], publisher: Publisher) -> None:
    """makes a request to the mqtt publisher

    Args:
        ups_list (dict[str, Ups]): list of ups to publish about
        publisher (Publisher): the mqtt publisher
    """
    for name, ups in ups_list.items():
        publisher.publish_ups_data(name, ups.get_dict())


def gracefull_exit() -> None:
    """gracefully close the module"""
    print("Closing...")
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

    for ups_config in ups_list.values():
        # get the config for the ups
        is_local = ups_config["is_local"]
        host = None
        port = None

        # if the ups is not local, make sure the host and port are
        # provided
        if not is_local:
            host, port = get_host_config(ups_config)

        ups = Ups(is_local, host, port)

        ups_dict[ups.name] = ups

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
        default="config/apcmqtt.yaml",
    )

    args = vars(parser.parse_args())

    if args["debug"]:
        LOGGER.setLevel(logging.DEBUG)

    try:
        UPS_DICT, PUBLISHER, DELAY = setup(args["config"])
    except MissingConfigError:
        utils.log_message(
            LOGGER,
            "Configuration file could not be found",
            logging.ERROR)

    try:
        loop(UPS_DICT, PUBLISHER, DELAY)
    except KeyboardInterrupt:
        gracefull_exit()
