from time import sleep
import paho.mqtt.client as mqtt

class Publisher:

    _client: mqtt.Client

    def __init__(self, user: str, password: str):
        self._client = mqtt.Client()
        self._client.username_pw_set(user, password)

    def connect(self, host: str, port: int = 1883) -> None:
        self._client.connect(host, port)

    def _publish(self, topic: str, payload: str) -> None:
        self._client.publish(topic, payload)

    def publish_ups_data(self, name:str, datapack: dict[str, str]) -> None:

        for key, value in datapack.items():
            try:
                self._publish(f"ups/{name}/{key}", str(value))
            except:
                foo = "bar"

            sleep(0.1)