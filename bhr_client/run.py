from bhr_client.rest import Client
import sys

def main():
    ident = sys.argv[1]

    c = Client(ident)
    c.run()

if __name__ == "__main__":
    main()
