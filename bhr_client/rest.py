import signal
import requests
import time
import json
import csv
import os

js_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

class Client:
    """BHR Client"""
    def __init__(self, host, session, ident=None):
        if ident:
            self.ident = ident
        self.host = host
        self.s = session

    @property
    def ident(self):
        raise Exception("ident is not set")

    def post_json(self, url, data):
        data = json.dumps(data)
        resp =  self.s.post(self.host + url, data, headers=js_headers)
        resp.raise_for_status()
        return resp.json()

    def get_json(self, url, params=None):
        resp = self.s.get(self.host + url, params=params)
        resp.raise_for_status()
        return resp.json()

    def block(self, cidr, source, why, duration=300, autoscale=0, skip_whitelist=0):
        """Send a block request to the BHR system

        :param cidr: The IP Address or CIDR network to block
        :param source: The source for this block. i.e., where the intel came from
        :param why: The reason for the block
        :param duration: The time to block in seconds, or a string like '1d'.  Accepted suffixes are y, mo, d, h, m, s.
        :param autoscale: Whether or not to auto scale the duration based on server side block history
        :param skip_whitelist: Whether or not to bypass the server side whitelist
        """

        record = {
            'cidr': cidr,
            'source': source,
            'why': why,
            'duration': duration,
            'autoscale': autoscale,
            'skip_whitelist': skip_whitelist,
        }
        resp = self.s.post(self.host + '/bhr/api/block', data=record)
        resp.raise_for_status()
        return resp.json()

    def unblock_now(self, cidr, why):
        """Send an unblock request to the BHR system

        :param cidr: The IP Address or CIDR network to unblock
        :param why: The reason for the block being removed
        """

        data = {
            "cidr": cidr,
            "why": why,
        }
        return self.post_json("/bhr/api/unblock_now", data=data)

    def get_list(self):
        """Return a the current block list as a list of dictionaries"""
        r = self.s.get(self.host + '/bhr/list.csv')
        return csv.DictReader(r.iter_lines())

    def set_unblocked(self, records):
        """Mark a block record as unblocked
        
        This is not meant to be called directly
        """
        ids = [r['id'] for r in records]
        data = {"ids":ids}
        return self.post_json('/bhr/api/set_unblocked_multi', data)

    def set_blocked(self, records):
        """Mark a block record as blocked
        
        This is not meant to be called directly
        """
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

    def query(self, cidr):
        """Return the block history for an address"

        :param cidr: The IP Address or CIDR network to look up
        """
        return self.get_json('/bhr/api/query/' + cidr)

    def stats(self):
        """Return Current block stats"""
        return self.get_json('/bhr/api/stats')

def login(host, token=None, username=None, password=None, ident=None):
    """Create an authenticated client object.  To authenticate pass either a token or a username + password.

    :param host: the URL to the BHR system
    :param token: A django-rest-framework api token
    :param username:
    :param password:
    :param ident: Ident to use for backend block entry tracking
    """
    s = requests.session()
    authenticated = False
    if token:
        s.headers["Authorization"] = "Token " + token
        authenticated = True
    if username and password:
        s.auth = (username, password)
        authenticated = True

    if not authenticated:
        raise Exception("token or (username + password) required")
    return Client(host, s, ident)

def login_from_env():
    """Create an authenticated client object using environment variables.  This simply calls :func:`login`.
    The environment variables looked at are:

        * ``BHR_HOST`` - mapped to host
        * ``BHR_TOKEN`` - mapped to token
        * ``BHR_USERNAME`` - mapped to username
        * ``BHR_PASSWORD`` - mapped to password
        * ``BHR_IDENT`` - mapped to ident
    """

    host = os.environ["BHR_HOST"]
    ident = os.environ.get("BHR_IDENT")
    token = os.environ.get("BHR_TOKEN")
    username = os.environ.get("BHR_USERNAME")
    password = os.environ.get("BHR_PASSWORD")
    return login(host, token, username, password, ident)
