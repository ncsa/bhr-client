#! /usr/local/env python
from bhr_client.rest import login_from_env
import argparse
import time

def main():
    bhr = login_from_env()
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help="Filename with the IPs (expect 1 per line)", required=True)
    parser.add_argument('--time', help="block time in seconds", required=True)
    parser.add_argument('--why', help="reason for the block", required=True)

    args = parser.parse_args()

    with open(args.file,"r") as f:
        for line.rstrip() in f:
            bhr.block(cidr=line, source="BHR Client Batch", why=args.why, duration=args.time)

if __name__ == "__main__":
    main()
