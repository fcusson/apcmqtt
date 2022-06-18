"""apcmqtt - apcupsd to mqtt translation layer

This modules monitors apcupsd continuously and updates an MQTT on the
changes of status

functions:
    main(): code entrypoint
"""

__version__ = "0.1.1"
__author__ = "Felix Cusson"

from apcmqtt.apc import Ups
from apcmqtt.mqtt import Publisher
import yaml
from apcmqtt.exceptions import MissingConfigError, ConfigurationError
import time
import threading


CONFIG_FILE = "config/apcmqtt.yaml"

def setup() -> tuple[dict[str, Ups], Publisher]:
    """general setup before starting the main loop of the script"""

    # get the config information
    try:
        with open(CONFIG_FILE, mode='r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as exc:
        raise MissingConfigError(
            "The configuration file could not be found"
        ) from exc

    ups_dict = find_ups(config["ups"])

    #get the config for the mqtt broker
    try:
        user = config["mqtt"]["user"]
        password = config["mqtt"]["password"]
        host = config["mqtt"]["host"]
        port = config["mqtt"]["port"]
    except KeyError as exc:
        raise ConfigurationError(
            "Missing configuration element", str(exc)
        ) from exc

    # create the mqtt_publisher instance
    publisher = Publisher(user, password, host, port)
    #publisher.publish_ups_data(ups.name, ups.get_dict())

    return ups_dict, publisher

def loop(ups_list: dict[str, Ups], publisher: Publisher) -> None:
    """main loop of the script that will execute until stopped"""
    while True:
        for name, ups in ups_list.items():
            publisher.publish_ups_data(name, ups.get_dict())
        time.sleep(10)

def gracefull_exit() -> None:
    """manages exiting the script"""
    print("Closing...")
    exit(0)

def find_ups(ups_list: dict) -> dict[str,Ups]:
    """finds the different ups configured in config and returns a
    dictionary of them
    """
    ups_dict = {}

    for ups_config in ups_list.values():
        #get the config for the ups
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
    """returns the host and port from a yaml config file"""
    try:
        host = ups["host"]
        port = ups["port"]
    except KeyError as exc:
        raise ConfigurationError(
            "Missing configuration element", str(exc)
        ) from exc

    return (host, port)




if __name__ == "__main__":
    UPS_DICT, PUBLISHER = setup()

    try:
        loop(UPS_DICT, PUBLISHER)
    except KeyboardInterrupt:
        print("closing...")
        exit(0)