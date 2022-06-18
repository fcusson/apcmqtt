"""apcmqtt - apcupsd to mqtt translation layer

This modules monitors apcupsd continuously and updates an MQTT on the
changes of status

functions:
    main(): code entrypoint
"""

from apcmqtt.apc import Ups
from apcmqtt.mqtt import Publisher

def main():
    """code entrypoint"""

    # create the ups instance
    ups = Ups()

    # create the mqtt_publisher instance
    publisher = Publisher("kuma", "Folder#502")
    publisher.connect("192.168.0.50")

    ups.update()
    publisher.publish_ups_data(ups.name, ups.dict())

if __name__ == "__main__":
    main()