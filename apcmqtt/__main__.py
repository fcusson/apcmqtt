"""apcmqtt - apcupsd to mqtt translation layer

This modules monitors apcupsd continuously and updates an MQTT on the
changes of status

functions:
    main(): code entrypoint
"""

from time import sleep
from apcmqtt.apc import Ups
from apcmqtt.mqtt import Publisher

def setup() -> tuple[Ups, Publisher]:
    """code entrypoint"""

    # create the ups instance
    ups = Ups(is_local=True)
    ups.update()

    # create the mqtt_publisher instance
    publisher = Publisher("kuma", "Folder#502", "192.168.0.50")
    #publisher.publish_ups_data(ups.name, ups.get_dict())
    #publisher._publish("dev/test", "test")

    return ups, publisher

def loop(ups: Ups, publisher: Publisher) -> None:
    while True:
        print("Hello World!")
        sleep(1)

def quit() -> None:
    print("Closing...")
    exit(0)

if __name__ == "__main__":
    ups, publisher = setup()

    try:
        loop(ups, publisher)
    except KeyboardInterrupt:
        print("closing...")
        exit(0)