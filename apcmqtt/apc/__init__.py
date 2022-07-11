"""control elements of an APCUPSD compatible UPS

Classes:
    Ups
"""
from datetime import datetime
import logging
import subprocess
import apcmqtt.utils as utils

from apcmqtt.exceptions import DependencyError, ApcAccessConnectionError

_REMOVE_LIST = [
    " Volts",
    " Seconds",
    " Percent",
    " Minutes",
    " Watts"
]

LOGGER = logging.getLogger(__name__)


class Ups:
    """An instance of a APCUPSD compatible UPS

    Attributes:
        name (str): name of the ups
        status (str): latest known status of the UPS
        time_left (float): time in minute left on the ups
        battery_charge (float): percentage of the battery charge
        datapack (dict[str, str]: dictionary of the remaining attributes
            from the ups
        is_local (bool): True if the apcupsd instance is located on the
            same machine as the script
        host (str): address to the acpupsd instance
        port (int): port number to contact the apcupsd instance on


    Methods:
        update()
        get_dict()
        get_ups_status()"""

    name: str
    status: str
    time_left: float
    battery_charge: float
    datapack: dict[str, str]
    is_local: bool
    host: str
    port: int

    def __init__(
            self,
            name: str,
            is_local: bool = True,
            host: str = None,
            port: int = None
    ) -> None:
        """creates an instance of a apcupsd connection object

        Args:
            is_local (bool, optional): True if the apcupsd instance is
                local. Defaults to True.
            host (str, optional): address to connect to the apcupsd
                instance. Defaults to None.
            port (int, optional): port to communicate on to the apcupsd
                instance. Defaults to None.
        """

        utils.log_message(
            LOGGER,
            f"initiating, apc instance for {name}",
            logging.DEBUG,
        )

        self.is_local = is_local
        self.host = host
        self.port = port
        self.name = name

        # placeholder attribute
        self.status = None
        self.time_left = None
        self.battery_charge = None
        self.datapack = {}

        try:
            self.update()
        except (ApcAccessConnectionError, DependencyError):
            url = f"{self.host}:{self.port}" if self.is_local else "localhost"
            utils.log_message(
                LOGGER,
                f"Unable to connect to apcaccess @{url}",
                logging.WARNING,
            )

    def __str__(self) -> str:
        """returns a string representation of the ups instance

        Returns:
            str: returns a line for each attributes returned by
                apcaccess
        """

        result = f"Name: {self.name}"
        result += f"\nStatus: {self.status}"
        result += f"\nTime Left: {self.time_left}"
        result += f"\nBattery Charge: {self.battery_charge}"

        for key, value in self.datapack.items():
            result += f"\n{key}: {value}"

        return result

    def update(self) -> None:
        """fetches the status of the ups to update the instance"""
        self.datapack = self.get_ups_status()

        self.name = self.datapack.pop("upsname")
        self.status = self.datapack.pop("status")
        self.time_left = self.datapack.pop("timeleft")
        self.battery_charge = self.datapack.pop("bcharge")

    def get_dict(self) -> dict[str, str]:
        """get a dictionary containing all the keys and values to
        publish

        Returns:
            dict[str, str]: a dictionary containing the topics for mqtt
            as key and the message for the topic as value
        """
        result = {
            "status": self.status,
            "time_left": self.time_left,
            "battery_charge": self.battery_charge,
        }

        result.update(self.datapack)

        result["keys"] = str(list(result.keys()))

        return result

    def get_ups_status(self) -> dict[str, str]:
        """retreives the ups status from the computer and returns a
        dictionary of the attributes

        Returns:
            dict(str,str): a dictionnary containing the data descriptor as
            key and its value as value
        """
        result = {}

        try:

            query = "/usr/sbin/apcaccess" if self.is_local else \
                ["/usr/sbin/apcaccess", "-h", f"{self.host}:{self.port}"]

            status = subprocess.check_output(query).decode("ascii")

        except FileNotFoundError as exc:
            raise DependencyError(
                "apcupsd not found. Install Dependencies or change to correct"
                "location in config"
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise ApcAccessConnectionError(
                "Unable to connect to remote apcupsd agent"
            ) from exc

        for line in status.split('\n'):

            if line == "":
                continue

            key, value = line.split(": ")

            # clean up values
            key = key.strip().lower()
            value = _clean_value(value)

            result[key] = value

        return result


def _clean_value(value: str) -> str:
    """remove unnecessary key-words from a value

    Args:
        value (str): the value to clean

    Returns:
        str: value cleaned
    """

    for word in _REMOVE_LIST:

        if word in value:
            value = value.replace(word, '')

    if utils.is_date(value):
        value = ' '.join(value.split(' ')[:2])

    return value.strip()
