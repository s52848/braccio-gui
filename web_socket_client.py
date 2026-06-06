from threading import Lock, Thread
from time import sleep
from typing import Callable

from websockets.sync.client import connect


class WebSocketClient:
    def __init__(self):
        self._latest_vector: str | None = None
        self._lock = Lock()
        self._on_connection: Callable[[], None]
        self._on_reconnecting: Callable[[], None]

        Thread(target=self._establish_connection, daemon=True).start()

    def send_vector(self, vector: str) -> None:
        with self._lock:
            self._latest_vector = vector

    def subscribe_on_connection(self, callback: Callable[[], None]) -> None:
        self._on_connection = callback

    def subscribe_on_reconnecting(self, callback: Callable[[], None]) -> None:
        self._on_reconnecting = callback

    def _establish_connection(self) -> None:
        while True:
            try:
                self._try_establish_connection()
            except Exception:
                self._on_reconnecting()

    def _try_establish_connection(self) -> None:
        with connect("ws://10.42.0.1:8765", open_timeout=1) as websocket:
            self._on_connection()

            while True:
                sleep(0.1)

                with self._lock:
                    vector = self._latest_vector
                    self._latest_vector = None

                if vector is None:
                    continue

                print("SENDING: ", vector)
                websocket.send(vector)
