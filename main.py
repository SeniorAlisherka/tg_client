from main_logic.tg_client import TelegramClient


def main():
    client = TelegramClient()
    client.run()


if __name__ == "__main__":
    main()
