"""module containing classes to manage mqtt methods

Classes:
    Publisher
"""

import paho.mqtt.publish as publish


class Publisher:
    """Publishes topics on an mqtt broker"""

    _auth: dict[str, str] = {}
    _host: str = None
    _port: str = 1883

    def __init__(self, user: str, password: str, host: str, port: int = 1883):
        self._auth["username"] = user
        self._auth["password"] = password
        self._host = host
        self._port = port

    def _publish(self, topic: str, payload: str) -> None:
        publish.single(
            topic=topic,
            payload=payload,
            qos=0,
            retain=True,
            hostname=self._host,
            port=self._port,
            auth=self._auth,
        )

    def publish_ups_data(self, name: str, datapack: dict[str, str]) -> None:

        for key, value in datapack.items():
            print(f"ups/{name}/{key}: {value}")
            self._publish(f"ups/{name}/{key}", str(value))
