# src/datatypes/tg_client.py
import json
import os
import sys
import threading
from ctypes import CDLL, CFUNCTYPE, c_char_p, c_double, c_int
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from src.static_instances import event_dispatchers
import src.static_instances.menus as menus


class TelegramClient:
    def __init__(self) -> None:
        load_dotenv()
        self.api_id = int(os.getenv("TG_API_ID"))
        self.api_hash = os.getenv("TG_API_HASH")

        self._load_library()
        self._setup_functions()
        self._setup_logging()

        self.client_id = self._td_create_client_id()

        self.auth_done = threading.Event()
        self.authorized = threading.Event()
        self.closed = threading.Event()
        self.current_menu = menus.main
        self.menu_event = threading.Event()
        self.state = {}
        self.current_task_cancelled = False
        self.current_task_id = 0  # for tracking long tasks with cancel

    def _load_library(self) -> None:
        lib_path = os.getenv("TDLIB_PATH")
        self.tdjson = CDLL(lib_path)

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
        dev_mode = eval(os.getenv("DEV_MODE"))
        if not dev_mode:
            verbosity_level = 0  # in production

        @self.log_message_callback_type
        def on_log_message_callback(verbosity_level, message) -> None:
            if verbosity_level == 0:  # handle only fatal errors
                sys.exit(f"\nTDLib fatal error: {message.decode('utf-8')}")
                print(f"\nTDLib fatal error: {message.decode('utf-8')}")
            elif verbosity_level == 1:
                print(f"\nTDLib error: {message.decode('utf-8')}")

        self._on_log_message_callback = on_log_message_callback

        self._td_set_log_message_callback(
            3, on_log_message_callback
        )  # send logs with verbosity <= 3 (fatal, errors, warnings, debug) to callback
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
        # print("\nSending:", query)
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
            # print("\nReceived:", result.decode("utf-8"))
            return json.loads(result.decode("utf-8"))
        return None

    def run(self) -> None:
        try:
            td_thread = threading.Thread(target=self._tdlib_loop, daemon=True)
            td_thread.start()

            # Wait until auth finishes (success OR failure)
            self.auth_done.wait()

            if self.authorized.is_set():
                menu_thread = threading.Thread(target=self._menu_loop, daemon=True)
                menu_thread.start()

            self.closed.wait()

        except KeyboardInterrupt:
            print("\n🛑 Ctrl+C received, shutting down...")
            self.send({"@type": "close"})
            self.closed.wait()

    def _tdlib_loop(self) -> None:
        event_dispatchers_by_type = {
            "updateAuthorizationState": event_dispatchers.updateAuthorizationState,
            "authorizationStateWaitPassword": event_dispatchers.authorizationStateWaitPassword,
            "error": event_dispatchers.error,
            "user": event_dispatchers.user,
            "chats": event_dispatchers.chats,
            "chat": event_dispatchers.chat,
            "chatMembers": event_dispatchers.chatMembers,
            "users": event_dispatchers.users,
            "supergroup": event_dispatchers.supergroup,
        }

        self.send({"@type": "getOption", "name": "version"})

        while True:
            event = self.receive(timeout=1.0)
            if not event:
                continue

            event_type = event["@type"]
            event_dispatcher = event_dispatchers_by_type.get(event_type)

            if event_dispatcher:
                event_dispatcher.handle_event(self, event)

    def _menu_loop(self):
        while True:
            self.menu_event.clear()
            self.current_menu.render(self)
            choice = input("> ").strip().lower()
            os.system("clear")
            self.current_menu.handle_choice(self, choice)
            self.menu_event.wait()

    def set_menu(self, menu):
        self.current_menu = menu
        self.menu_event.set()

    def start_cancel_listener(self):
        self.current_task_cancelled = False

        def _listen():
            while not self.current_task_cancelled:
                choice = input().strip().lower()
                if choice == "c":
                    print("\n❌ Operation cancelled.")
                    self.current_task_cancelled = True
            self.menu_event.set()

        threading.Thread(target=_listen, daemon=True).start()

    def is_current_task_cancelled(self) -> bool:
        return self.current_task_cancelled

    def stop_cancel_listener(self):
        self.current_task_cancelled = True

    def ask_for_enter(self):
        print("\nPress Enter to continue...")
