"""module containing classes to manage mqtt methods

Classes:
    Publisher
"""

import logging
import paho.mqtt.publish as publish

from apcmqtt.exceptions import MqttConnectionError, ApcAccessConnectionError
import apcmqtt.utils as utils

LOGGER = logging.getLogger(__name__)


class Publisher:
    """Publishes topics on an mqtt broker

    Attributes:
        host (str): address of the mqtt broker
        port (int): port to communicate to the mqtt broker on

    Methods:
        publish_ups_date(name: str, datapack: dict[str, str])"""

    _auth: dict[str, str] = {}
    host: str = None
    port: int = 1883
    root_topic: str = None

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int = 1883,
        root_topic: str = "ups"
    ) -> None:

        self._auth["username"] = user
        self._auth["password"] = password
        self.host = host
        self.port = port
        self.root_topic = root_topic

    def __str__(self) -> str:
        return f"{self.host}:{self.port} -> {self.root_topic}"

    def _publish(self, topic: str, payload: str) -> None:
        try:
            publish.single(
                topic=topic,
                payload=payload,
                qos=0,
                retain=True,
                hostname=self.host,
                port=self.port,
                auth=self._auth,
            )
        except TimeoutError as exc:
            raise MqttConnectionError from exc
        except (
            MqttConnectionError,
            ApcAccessConnectionError,
        ) as exc:
            raise exc

    def publish_ups_data(self, name: str, datapack: dict[str, str]) -> None:
        """publishes the different values in the datapack for the ups
        name provided

        Args:
            name (str): name of the ups
            datapack (dict[str, str]): dictionnary containing the
                different topics (keys) and message (values)
        """

        for key, message in datapack.items():

            topic = f"{self.root_topic}/{name}/{key}"
            utils.log_message(
                LOGGER,
                f"publishing {str(message)} on {topic}",
                logging.DEBUG
            )
            self._publish(topic, str(message))
