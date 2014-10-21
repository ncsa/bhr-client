import signal
import requests
import time
import json
import csv

js_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

class Client:
    def __init__(self, ident=None):
        self.ident = ident
        s = requests.session()
        s.headers["Authorization"]="Token 003f656f26cadb7f0d4cfdf2771fc337010e3400"
        self.s = s

    def post_json(self, url, data):
        data = json.dumps(data)
        return self.s.post('http://localhost:8000' + url, data, headers=js_headers).json()

    def block(self, cidr, source, why, duration=300, skip_whitelist=0):
        record = {
            'cidr': cidr,
            'source': source,
            'why': why,
            'duration': duration,
            'skip_whitelist': skip_whitelist,
        }
        return self.s.post('http://localhost:8000/bhr/api/block', data=record).json()

    def get_list(self):
        r = self.s.get('http://localhost:8000/bhr/list.csv')
        return csv.DictReader(r.iter_lines())

    def set_unblocked(self, records):
        ids = [r['id'] for r in records]
        data = json.dumps({"ids":ids})
        resp = self.s.post('http://localhost:8000/bhr/api/set_unblocked_multi', data=data, headers=js_headers).json()
        return resp

    def set_blocked(self, records):
        ids = [r['id'] for r in records]
        data = json.dumps({"ids":ids})
        resp = self.s.post('http://localhost:8000/bhr/api/set_blocked_multi/%s' % self.ident, data=data,headers=js_headers).json()
        return resp

    def get_block_queue(self):
        return self.s.get('http://localhost:8000/bhr/api/queue/%s' % self.ident).json()

    def get_unblock_queue(self):
        return self.s.get('http://localhost:8000/bhr/api/unblock_queue/%s' % self.ident).json()

    def get_expected(self, source=None):
        params = {'source': source}
        return self.s.get('http://localhost:8000/bhr/api/expected_blocks/', params=params).json()

    def unblock_now(self, cidr, why):
        data = {
            "cidr": cidr,
            "why": why,
        }
        return self.post_json("/bhr/api/unblock_now", data=data)
