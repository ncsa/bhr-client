import signal
import time
import random
import arrow
import datetime

WATCHDOG_TIMEOUT = 60 #seconds
UNBLOCK_INTERVAL = 30 #seconds

def shift_backwards(ts, minutes=5):
    """parse and shift a timestamp backwards 5 minutes"""
    # I hate timestamps
    nt = arrow.get(ts) - datetime.timedelta(minutes=minutes)
    value = nt.isoformat()
    # https://github.com/tomchristie/django-rest-framework/blob/cf5d401a0e60948ed0b3ad384c3f76fc30c3e222/rest_framework/fields.py#L1154
    if value.endswith('+00:00'):
        value = value[:-6] + 'Z'
    return value

class DummyStdoutBlocker:
    def __init__(self):
        pass

    def block_many(self, records):
        for r in records:
            print time.ctime(), "block", r['cidr']

    def unblock_many(self, records):
        for r in records:
            print time.ctime(), "unblock", r['block']['cidr']

class BlockManager:
    def __init__(self, client, blocker):
        self.client = client
        self.blocker = blocker
        self._added_since = '2014-09-01'

    def do_block(self):
        records = self.client.get_block_queue(timeout=UNBLOCK_INTERVAL+2, added_since=self._added_since)
        if records:
            self.blocker.block_many(records)
            self.client.set_blocked(records)
            self._added_since = shift_backwards(records[-1]['added'])
        return bool(records)

    def do_unblock(self):
        records = self.client.get_unblock_queue()
        if records:
            self.blocker.unblock_many(records)
            self.client.set_unblocked(records)
        return bool(records)

    def block_all_expected(self):
        """Block all addresses that are expected to be blocked
           This is to be used for stateless backends like ExaBGP
        """
        blocks = self.client.get_list()
        return self.blocker.block_many(blocks)

    def run_once(self):
        did = self.do_unblock()
        did = did or self.do_block()
        return did

    def run(self):
        """Run the blocker, blocking and unblocking as needed"""
        since_unblock = 0
        while True:
            blocked = unblocked = False
            signal.alarm(self.client.timeout + WATCHDOG_TIMEOUT)
            if time.time() - since_unblock > UNBLOCK_INTERVAL:
                unblocked = self.do_unblock()
                since_unblock = time.time()
            blocked = self.do_block()
            if not (blocked or unblocked):
                time.sleep(0.1)
