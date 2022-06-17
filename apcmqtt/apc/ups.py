"""control elements of an APCUPSD compatible UPS

Classes:
    Ups
"""

import subprocess

class Ups:
    """An instance of a APCUPSD compatible UPS"""

    datapack: dict[str, str]

    def __init__(self, ) -> None:
        pass

    def update(self) -> None:
        """fetches the status of the ups to update the instance"""


def get_ups_status() -> dict[str, str]:
    """retreives the ups status from the computer and returns a
    dictionary of the attributes

    Returns:
        dict(str,str): a dictionnary containing the data descriptor as
        key and its value as value
    """
    status = subprocess.check_output("/usr/sbin/apcaccess")

    for line in status.split("\n"):
        print(line)
