from bhr_client.rest import Client
import sys

ident = sys.argv[1]

c = Client(ident)
c.run()
