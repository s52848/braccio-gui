from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

from web_socket_client import WebSocketClient

TEST_VECTORS_REGISTRY: dict[str, str] = {
    "Base min": "5,0,90,90,90,90,73",
    "Base mid": "5,90,90,90,90,90,73",
    "Base max": "5,180,90,90,90,90,73",
    "Post base": "5,90,90,90,90,90,73",
    "Shoulder min": "5,90,15,90,90,90,73",
    "Shoulder mid": "5,90,90,90,90,90,73",
    "Shoulder max": "5,90,165,90,90,90,73",
    "Post shoulder": "5,90,90,90,90,90,73",
    "Elbow min": "5,90,90,0,90,90,73",
    "Elbow mid": "5,90,90,90,90,90,73",
    "Elbow max": "5,90,90,180,90,90,73",
    "Post elbow": "5,90,90,90,90,90,73",
    "Wrist vertical min": "5,90,90,90,0,90,73",
    "Wrist vertical mid": "5,90,90,90,90,90,73",
    "Wrist vertical max": "5,90,90,90,180,90,73",
    "Post wrist vertical": "5,90,90,90,90,90,73",
    "Wrist rotation min": "5,90,90,90,90,0,73",
    "Wrist rotation mid": "5,90,90,90,90,90,73",
    "Wrist rotation max": "5,90,90,90,90,180,73",
    "Post wrist rotation": "5,90,90,90,90,90,73",
    "Gripper min": "5,90,90,90,90,90,73",
    "Gripper mid": "5,90,90,90,90,90,42",
    "Gripper max": "5,90,90,90,90,90,10",
}


class Controller(Widget):
    status = ObjectProperty(None)
    test_logs = ObjectProperty(None)
    base = ObjectProperty(None)
    shoulder = ObjectProperty(None)
    elbow = ObjectProperty(None)
    wrist_vertical = ObjectProperty(None)
    wrist_rotation = ObjectProperty(None)
    gripper = ObjectProperty(None)
    screen_manager = ObjectProperty(None)

    def __init__(self, client: WebSocketClient, **kwargs) -> None:
        super().__init__(**kwargs)

        self._client = client
        self._test_events: list = []
        self._retry_count: int = 0

        self._client.subscribe_on_connection(self.connected_task)
        self._client.subscribe_on_reconnecting(self.reconnecting_task)
        self._client.start()

    def raise_menu(self) -> None:
        self.cancel_test()

        self.screen_manager.current = "Menu"

    def raise_test(self) -> None:
        def send_test_vector(angle: str, vector: str) -> None:
            self.test_logs.text += f"{angle}\n"
            self._client.send_vector(vector)

        self.screen_manager.current = "Test"

        self._test_events = [
            Clock.schedule_once(
                lambda dt, a=angle, v=values: send_test_vector(a, v),
                i * 2,
            )
            for i, (angle, values) in enumerate(TEST_VECTORS_REGISTRY.items())
        ]

    def cancel_test(self) -> None:
        self.test_logs.text = ""

        for event in self._test_events:
            event.cancel()

        self._test_events.clear()

    def raise_manual(self) -> None:
        self.screen_manager.current = "Manual"

        self.base.value = 90
        self.shoulder.value = 45
        self.elbow.value = 180
        self.wrist_vertical.value = 180
        self.wrist_rotation.value = 90
        self.gripper.value = 10

        self.send_angle_vector()

    def raise_automatic(self) -> None:

        self.screen_manager.current = "Automatic"

    def send_angle_vector(self) -> None:
        vector = (
            1,
            int(self.base.value),
            int(self.shoulder.value),
            int(self.elbow.value),
            int(self.wrist_vertical.value),
            int(self.wrist_rotation.value),
            int(self.gripper.value),
        )

        cmd = ",".join(map(str, vector))

        self._client.send_vector(cmd)

    def reconnecting_task(self) -> None:
        TEXTS: dict[int, str] = {
            0: "Reconnecting.",
            1: "Reconnecting..",
            2: "Reconnecting...",
        }

        self.status.color = (1, 1, 0, 1)
        self.status.text = TEXTS.get(self._retry_count)
        self._retry_count = self._retry_count + 1 if self._retry_count < 2 else 0

    def connected_task(self) -> None:
        self.status.text = "Connected"
        self.status.color = (0, 1, 0, 1)
        self._retry_count = 0


class Gui(App):
    def build(self) -> Controller:
        Builder.load_file("view.kv")

        return Controller(WebSocketClient())


if __name__ == "__main__":
    Gui().run()
