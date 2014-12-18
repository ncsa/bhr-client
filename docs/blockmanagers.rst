Writing a block manager
=======================

In the BHR system blocks are handled by an external component called a blocker.

:class:`bhr_client.block_manager.BlockManager` Takes a
:class:`bhr_client.rest.Client` and a Blocker object, and blocks/unblocks things as needed.

To implement a blocker, simply write a class that implements ``block_many`` and ``unblock_many`` methods.

This is the simplest example, it just prints out what should be blocked and unblocked to stdout.  A real blocker
would add firewall rules, ACL entries, etc.

::

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

To use the blocker, you would write a main function like::

    from bhr_client.rest import login_from_env
    def main():
        client = login_from_env()
        blocker = DummyStdoutBlocker()
        m = BlockManager(client, blocker)
        m.run()

.. autoclass:: bhr_client.block_manager.BlockManager
    :members: run
