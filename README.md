Work in progress client for BHR site.

See http://bhr-client.readthedocs.org/en/latest/ for full docs

    $ export BHR_TOKEN=abc91639287637189236193671983619783619c4
    $ export BHR_HOST=http://localhost:8000
    $ python
    >>> from bhr_client.rest import login_from_env
    >>> c = login_from_env()
    >>> c.stats()
    {u'current': 3650, u'expected': 3606, u'block_pending': 1, u'unblock_pending': 45}
    >>> c.query("192.168.254.254")
    []
    >>> c.block(cidr='192.168.254.254', source='readme', why='because!', duration=300)
    {u'added': u'2014-11-14T15:30:24.785Z',
     u'cidr': u'192.168.254.254/32',
     u'set_blocked': u'http://localhost:8000/bhr/api/blocks/359147/set_blocked/',
     u'skip_whitelist': False,
     u'source': u'readme',
     u'unblock_at': u'2014-11-14T15:35:24.784Z',
     u'url': u'http://localhost:8000/bhr/api/blocks/359147/',
     u'who': u'admin',
     u'why': u'because!'}
    >>> c.query("192.168.254.254")
    [{u'added': u'2014-11-14T15:30:24.785Z',
      u'cidr': u'192.168.254.254/32',
      u'set_blocked': u'http://localhost:8000/bhr/api/blocks/359147/set_blocked/',
      u'skip_whitelist': False,
      u'source': u'readme',
      u'unblock_at': u'2014-11-14T15:35:24.784Z',
      u'url': u'http://localhost:8000/bhr/api/blocks/359147/',
      u'who': u'admin',
      u'why': u'because!'}]


## Example Setup 

This example assumes the existence of a file `blocks.txt` full of block addresses - one per line.

```sh
python -m venv env
./env/scripts/activate
python setup.py install
bhr-client-batch --file blocks.txt --why "Malicious activity." --time "24mo"
```

