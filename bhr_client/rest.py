import signal
import requests
import time
import json
import csv

js_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

class Client:
    def __init__(self, ident=None):
        if ident:
            self.ident = ident
        s = requests.session()
        s.headers["Authorization"]="Token 003f656f26cadb7f0d4cfdf2771fc337010e3400"
        self.host = 'http://localhost:8000'
        self.s = s

    @property
    def ident(self):
        raise Exception("ident is not set")

    def post_json(self, url, data):
        data = json.dumps(data)
        return self.s.post(self.host + url, data, headers=js_headers).json()

    def get_json(self, url, params=None):
        return self.s.get(self.host + url, params=params).json()

    def block(self, cidr, source, why, duration=300, skip_whitelist=0):
        record = {
            'cidr': cidr,
            'source': source,
            'why': why,
            'duration': duration,
            'skip_whitelist': skip_whitelist,
        }
        return self.s.post(self.host + '/bhr/api/block', data=record).json()

    def get_list(self):
        r = self.s.get('http://localhost:8000/bhr/list.csv')
        return csv.DictReader(r.iter_lines())

    def set_unblocked(self, records):
        ids = [r['id'] for r in records]
        data = {"ids":ids}
        return self.post_json('/bhr/api/set_unblocked_multi', data)

    def set_blocked(self, records):
        ids = [r['id'] for r in records]
        data = {"ids":ids}
        return self.post_json('/bhr/api/set_blocked_multi/' + self.ident, data)
        return resp

    def get_block_queue(self):
        return self.get_json('/bhr/api/queue/' + self.ident)

    def get_unblock_queue(self):
        return self.get_json('/bhr/api/unblock_queue/' + self.ident)

    def get_expected(self, source=None):
        params = {'source': source}
        return self.get_json('/bhr/api/expected_blocks/', params=params)

    def unblock_now(self, cidr, why):
        data = {
            "cidr": cidr,
            "why": why,
        }
        return self.post_json("/bhr/api/unblock_now", data=data)
