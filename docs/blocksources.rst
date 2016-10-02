Block Sources
==============

Blocking and unblocking addresses based on an intel source is a common task, so there is a helper class called 
:class:`bhr_client.source_blocker.SourceBlocker`

To implement a source blocker, simply write a class that subclasses :class:`bhr_client.source_blocker.SourceBlocker`

This example blocks addresses found in the DataPlane.org SSH Password Authentication feed.

::

    from bhr_client.source_blocker import SourceBlocker
    from bhr_client.rest import login_from_env
    import requests


    class DataplaneBlocker(SourceBlocker):
        source = 'dataplane'
        must_exist = True
        duration = 0

        def get_records(self):
            blocks = []
            for line in requests.get("https://www.dataplane.org/sshpwauth.txt").iter_lines():
                if line.startswith("#"):
                    continue
                parts = line.split("|")
                parts = [x.strip() for x in parts]
                if len(parts) != 5:
                    continue
                asn, asname, saddr, utc, category = parts
                blocks.append({
                    'cidr': saddr,
                    'why': 'DataPlane SSH pwauth feed',
                })
            return blocks


To use the blocker, you would write a main function like::

    from bhr_client.rest import login_from_env
    def main():
        client = login_from_env()
        s = DataplaneBlocker(client)
        s.run()

To keep the BHR system in sync with the source, set ``must_exist`` to ``True``
and ``duration`` to ``0``.  If the intel feed only contains daily updates, you
would set ``must_exist`` to ``False`` and ``duration`` to something like `7d`.

.. autoclass:: bhr_client.source_blocker.SourceBlocker
    :members: get_records, run
