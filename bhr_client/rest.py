import signal
import requests
import time
import json

js_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

class DummyStdoutBlocker:
    def __init__(self):
        pass

    def block_many(self, records):
        for r in records:
            print time.ctime(), "block", r['cidr']

    def unblock_many(self, records):
        for r in records:
            print time.ctime(), "unblock", r['block']['cidr']

class Client:
    def __init__(self, ident, blocker=DummyStdoutBlocker()):
        self.ident = ident
        s = requests.session()
        s.headers["Authorization"]="Token 003f656f26cadb7f0d4cfdf2771fc337010e3400"
        self.s = s
        self.blocker = blocker

    def set_unblocked(self, records):
        ids = [r['id'] for r in records]
        data = json.dumps({"ids":ids})
        resp = self.s.post('http://localhost:8000/bhr/api/set_unblocked_multi', data=data, headers=js_headers).json()

    def set_blocked(self, records):
        ids = [r['id'] for r in records]
        data = json.dumps({"ids":ids})
        resp = self.s.post('http://localhost:8000/bhr/api/set_blocked_multi/%s' % self.ident, data=data,headers=js_headers).json()

    def do_block(self):
        signal.alarm(30)
        records = self.s.get('http://localhost:8000/bhr/api/queue/%s' % self.ident).json()
        if records:
            self.blocker.block_many(records)
            self.set_blocked(records)
        return bool(records)

    def do_unblock(self):
        signal.alarm(30)
        records = self.s.get('http://localhost:8000/bhr/api/unblock_queue/%s' % self.ident).json()
        if records:
            self.blocker.unblock_many(records)
            self.set_unblocked(records)
        return bool(records)

    def run(self):
        x = 0
        while True:
            did = self.do_block()
            if x % 10 == 0:
                did = did or self.do_unblock()
            if not did:
                x += 1
                time.sleep(2)
            else:
                time.sleep(.01)
