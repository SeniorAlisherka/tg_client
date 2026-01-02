import json
import os
import sys
from ctypes import CDLL, CFUNCTYPE, c_char_p, c_double, c_int
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from main_logic.utils import handlers
import threading

load_dotenv()


class TelegramClient:

    def __init__(self) -> None:
        self.api_id = int(os.getenv("TG_API_ID"))
        self.api_hash = str(os.getenv("TG_API_HASH"))
        self._load_library()
        self._setup_functions()
        self._setup_logging()
        self.client_id = self._td_create_client_id()
        self.authorized = threading.Event()
        self.got_response = threading.Event()
        self.closed = threading.Event()
        # menu logic
        self.menu = "_menu_main"
        self.channels = []
        self.pending_channels = 0

    def _load_library(self) -> None:
        base = os.path.dirname(__file__)
        tdjson_path = os.path.join(base, "libtdjson.dylib")
        self.tdjson = CDLL(tdjson_path)

    def _setup_functions(self) -> None:
        self._td_create_client_id = self.tdjson.td_create_client_id
        self._td_create_client_id.restype = c_int
        self._td_create_client_id.argtypes = []

        self._td_receive = self.tdjson.td_receive
        self._td_receive.restype = c_char_p
        self._td_receive.argtypes = [c_double]

        self._td_send = self.tdjson.td_send
        self._td_send.restype = None
        self._td_send.argtypes = [c_int, c_char_p]

        self._td_execute = self.tdjson.td_execute
        self._td_execute.restype = c_char_p
        self._td_execute.argtypes = [c_char_p]

        # Set log callback
        self.log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)
        self._td_set_log_message_callback = self.tdjson.td_set_log_message_callback
        self._td_set_log_message_callback.restype = None
        self._td_set_log_message_callback.argtypes = [
            c_int,
            self.log_message_callback_type,
        ]

    def _setup_logging(self, verbosity_level: int = 1) -> None:
        """Configure TDLib logging.

        Args:
            verbosity_level: 0-fatal, 1-errors, 2-warnings, 3+-debug
        """

        @self.log_message_callback_type
        def on_log_message_callback(verbosity_level, message) -> None:
            if verbosity_level == 0:  # handle only fatal errors
                sys.exit(f"TDLib fatal error: {message.decode('utf-8')}")
                print(f"TDLib fatal error: {message.decode('utf-8')}")
            elif verbosity_level == 1:
                print(f"TDLib error: {message.decode('utf-8')}")

        self._on_log_message_callback = on_log_message_callback

        self._td_set_log_message_callback(
            2, on_log_message_callback
        )  # send logs with verbosity <= 2 (fatal, errors, warnings) to callback
        self.execute(
            {"@type": "setLogVerbosityLevel", "new_verbosity_level": verbosity_level}
        )  # generate logs with verbosity <= 1 (fatal and errors only)

    def execute(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a synchronous TDLib request.

        Args:
            query: The request to execute

        Returns:
            Response from TDLib or None
        """
        query_json = json.dumps(query).encode("utf-8")
        result = self._td_execute(query_json)
        if result:
            return json.loads(result.decode("utf-8"))
        return None

    def send(self, query: Dict[str, Any]) -> None:
        """Send an asynchronous request to TDLib.

        Args:
            query: The request to send
        """
        query_json = json.dumps(query).encode("utf-8")
        self._td_send(self.client_id, query_json)

    def receive(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Receive a response or update from TDLib.

        Args:
            timeout: Maximum number of seconds to wait

        Returns:
            An update or response from TDLib, or None if nothing received
        """
        result = self._td_receive(timeout)
        if result:
            return json.loads(result.decode("utf-8"))
        return None

    def run(self) -> None:
        try:
            td_thread = threading.Thread(target=self._tdlib_loop, daemon=True)
            td_thread.start()
            self.authorized.wait()
            menu_thread = threading.Thread(target=self._menu_loop, daemon=True)
            menu_thread.start()
            self.closed.wait()
        except KeyboardInterrupt:
            print("\n🛑 Ctrl+C received, shutting down...")
            self.send({"@type": "close"})
            self.closed.wait()

    def _tdlib_loop(self) -> None:
        self.send({"@type": "getOption", "name": "version"})
        while True:
            event = self.receive(timeout=1.0)
            if event:
                self.handle(event)

    def handle(self, event):
        name = event["@type"]
        handler = getattr(handlers, f"on_{name}", None)

        if handler:
            handler(self, event)
        else:
            # print(f"Unhandled event: {name}")
            pass

    def _menu_loop(self) -> None:
        while True:
            try:
                handler = getattr(self, self.menu)
            except AttributeError:
                print("Unhandled menu:", self.menu)
                self.send({"@type": "close"})
                break
            handler()

    def _menu_main(self):
        print("\nMain menu:")
        print("1) Who am I?")
        print("2) Channels")
        print("q) Quit")

        choice = input("> ").strip().lower()

        if choice == "1":
            self._menu_main_1()

        elif choice == "2":
            self._menu_main_2()

        elif choice == "q":
            self._menu_main_q()

    def _menu_main_1(self):
        self.got_response.clear()
        self.send({"@type": "getMe", "@extra": "_menu_main"})
        self.got_response.wait()

    def _menu_main_2(self):
        self.got_response.clear()
        self.send({"@type": "getChats", "limit": 100000, "@extra": "_menu_main_2"})
        self.got_response.wait()
        self.menu = "_menu_channels"

    def _menu_main_q(self):
        self.send({"@type": "close"})

    def _menu_channels(self):
        print("\nChannels:")
        for i, ch in enumerate(self.channels, 1):
            print(f"{i}) {ch['title']}")
        print("b) Back")

        choice = input("> ").strip().lower()

        if choice == "b":
            self._menu_channels_b()

    def _menu_channels_b(self):
        self.menu = "_menu_main"
