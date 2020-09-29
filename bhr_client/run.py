from bhr_client.rest import login_from_env
from bhr_client.block_manager import BlockManager, DummyStdoutBlocker


def main():
    client = login_from_env()
    blocker = DummyStdoutBlocker()
    m = BlockManager(client, blocker)
    m.run()


if __name__ == "__main__":
    main()
