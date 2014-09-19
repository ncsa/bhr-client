from bhr_client.rest import Client
from bhr_client.block_manager import BlockManager, DummyStdoutBlocker
import sys

def main():
    ident = sys.argv[1]

    client = Client(ident)
    blocker = DummyStdoutBlocker()
    m = BlockManager(client, blocker)
    m.run()

if __name__ == "__main__":
    main()
