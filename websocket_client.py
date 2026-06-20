from threading import Lock, Thread
from time import sleep
from typing import Callable

from kivy.clock import Clock
from websockets.sync.client import connect


class WebSocketClient:
    def __init__(self):
        self._latest_message: str | None = None
        self._lock = Lock()
        self._on_connection: Callable[[], None]
        self._on_reconnecting: Callable[[], None]

    def start(self) -> None:
        Thread(target=self._establish_connection, daemon=True).start()

    def send_message(self, message: str) -> None:
        with self._lock:
            self._latest_message = message

    def subscribe_on_connection(self, callback: Callable[[], None]) -> None:
        self._on_connection = callback

    def subscribe_on_reconnecting(self, callback: Callable[[], None]) -> None:
        self._on_reconnecting = callback

    def _establish_connection(self) -> None:
        while True:
            try:
                self._try_establish_connection()
            except Exception:
                Clock.schedule_once(lambda dt: self._on_reconnecting(), 0)
                sleep(1)

    def _try_establish_connection(self) -> None:
        with connect("ws://10.42.0.1:8765", open_timeout=1) as websocket:
            Clock.schedule_once(lambda dt: self._on_connection(), 0)

            while True:
                sleep(0.1)

                with self._lock:
                    message = self._latest_message
                    self._latest_message = None

                if message is None:
                    continue

                websocket.send(message)
