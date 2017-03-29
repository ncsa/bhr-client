import signal
import requests
import time
import json
import csv
import os

js_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

DEFAULT_TIMEOUT = 30

class Client:
    """BHR Client"""
    def __init__(self, host, session, ident=None, timeout=DEFAULT_TIMEOUT):
        if ident:
            self.ident = ident
        self.host = host
        self.s = session
        self.timeout = timeout

    @property
    def ident(self):
        raise Exception("ident is not set")

    def post_json(self, url, data):
        data = json.dumps(data)
        resp =  self.s.post(self.host + url, data, headers=js_headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_json(self, url, params=None):
        extra_timeout = params['timeout'] if (params and 'timeout' in params) else 0
        resp = self.s.get(self.host + url, params=params, timeout=self.timeout + extra_timeout)
        resp.raise_for_status()
        return resp.json()

    def block(self, cidr, source, why, duration=300, autoscale=False, skip_whitelist=False, extend=False):
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
            'extend': extend,
        }
        resp = self.s.post(self.host + '/bhr/api/block', data=record, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def mblock(self, block_records):
        """Send a batch block request.
            :param block_records: A list of dictionaries whose keys are options to ':func:`block`'
            For example:
            block_records = [dict(
                cidr=ip,
                duration=30,
                source="test",
                why="testing",
            ) for ip in ips]
        """

        return self.post_json('/bhr/api/mblock', block_records)

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
        r = self.s.get(self.host + '/bhr/list.csv', timeout=self.timeout)
        r.raise_for_status()
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

    def get_block_queue(self, timeout=0, added_since=None):
        params = {
            "timeout": timeout,
            "added_since": added_since,
            }
        return self.get_json('/bhr/api/queue/' + self.ident, params)

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

def login(host, token=None, username=None, password=None, ident=None, ssl_no_verify=False, timeout=DEFAULT_TIMEOUT):
    """Create an authenticated client object.  To authenticate pass either a token or a username + password.

    :param host: the URL to the BHR system
    :param token: A django-rest-framework api token
    :param username:
    :param password:
    :param ident: Ident to use for backend block entry tracking
    :param ssl_no_verify: Disable SSL certificate verification
    """
    s = requests.session()
    authenticated = False
    if token:
        s.headers["Authorization"] = "Token " + token
        authenticated = True
    if username and password:
        s.auth = (username, password)
        authenticated = True

    if ssl_no_verify:
        s.verify = False

    if not authenticated:
        raise Exception("token or (username + password) required")
    return Client(host, s, ident, timeout)

def login_from_env():
    """Create an authenticated client object using environment variables.  This simply calls :func:`login`.
    The environment variables looked at are:

        * ``BHR_HOST`` - mapped to host
        * ``BHR_TOKEN`` - mapped to token
        * ``BHR_USERNAME`` - mapped to username
        * ``BHR_PASSWORD`` - mapped to password
        * ``BHR_IDENT`` - mapped to ident
        * ``BHR_SSL_NO_VERIFY`` - mapped to ssl_no_verify
    """

    host = os.environ["BHR_HOST"]
    ident = os.environ.get("BHR_IDENT")
    token = os.environ.get("BHR_TOKEN")
    username = os.environ.get("BHR_USERNAME")
    password = os.environ.get("BHR_PASSWORD")
    ssl_no_verify = bool(os.environ.get("BHR_SSL_NO_VERIFY"))
    timeout = int(os.environ.get("BHR_TIMEOUT", DEFAULT_TIMEOUT))
    return login(host, token, username, password, ident, ssl_no_verify, timeout)
