"""control elements of an APCUPSD compatible UPS

Classes:
    Ups
"""
from datetime import datetime
import subprocess

from apcmqtt.exceptions import DependencyError, ApcAccessConnectionError

_REMOVE_LIST = [
    " Volts",
    " Seconds",
    " Percent",
    " Minutes",
    " Watts"
]


class Ups:
    """An instance of a APCUPSD compatible UPS"""

    name: str
    status: str
    time_left: float
    battery_charge: float
    datapack: dict[str, str]
    is_local: bool
    host: str
    port: int

    def __init__(self, is_local: bool = True, host: str = None, port: int = None) -> None:
        self.is_local = is_local
        self.host = host
        self.port = port
        self.update()

    def __str__(self) -> str:

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
        result = {
            "name": self.name,
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

        except FileNotFoundError:
            raise DependencyError(
                "apcupsd not found. Install Dependencies or change to correct" +
                "location in config"
            )
        except subprocess.CalledProcessError:
            raise ApcAccessConnectionError(
                "Unable to connect to remote apcupsd agent"
            )

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

    for word in _REMOVE_LIST:

        if word in value:
            value = value.replace(word, '')

    if _is_date(value):
        value = ' '.join(value.split(' ')[:2])
        pass

    return value.strip()


def _is_date(string: str) -> bool:

    string = string.split(' ')[:2]
    string = ' '.join(string)

    try:
        datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False
