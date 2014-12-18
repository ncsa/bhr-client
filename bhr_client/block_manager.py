import signal
import time
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

    def do_block(self):
        records = self.client.get_block_queue()
        if records:
            self.blocker.block_many(records)
            self.client.set_blocked(records)
        return bool(records)

    def do_unblock(self):
        records = self.client.get_unblock_queue()
        if records:
            self.blocker.unblock_many(records)
            self.client.set_unblocked(records)
        return bool(records)

    def run_once(self):
        did = self.do_unblock()
        did = did or self.do_block()
        return did

    def run(self):
        """Run the blocker, blocking and unblocking as needed"""
        x = 0
        signal.alarm(30)
        self.do_unblock()
        while True:
            signal.alarm(30)
            did = self.do_block()
            if x % 10 == 0:
                did = did or self.do_unblock()
            if not did:
                x += 1
                time.sleep(2)
            else:
                time.sleep(.01)
