def chunk(l, n):
    """ Yield successive n-sized chunks from l.  """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class SourceBlocker:
    must_exist = False

    def __init__(self, client):
        self.client = client
        self.setup()

    @property
    def source(self):
        raise Exception("override source attribute")

    @property
    def duration(self):
        raise Exception("override duration attribute")

    def setup(self):
        pass

    def get_records(self):
        """Return a list of dictionaries of hosts to block.
        The dictionaries should contain ``cidr`` and ``why`` fields.
        They can also contain ``source`` and ``duration`` fields
        to override the class attributes.
        """
        raise NotImplementedError("Must implement get_records")

    def run(self):
        """Run the blocker, adding or removing blocks as needed"""

        wanted = set()
        current = self.client.get_expected(self.source)
        current_cidrs = set(x['cidr'] for x in current)
        block_records = []
        for record in self.get_records():
            cidr = record['cidr']
            if '/' not in cidr:
                cidr += '/32'
            wanted.add(cidr)
            if 'source' not in record:
                record['source'] = self.source
            if 'duration' not in record:
                record['duration'] = self.duration
            record['extend'] = True
            #If we are blocking indefinitely, and it is already blocked, do nothing
            if not record['duration'] and cidr in current_cidrs:
                continue
            block_records.append(record)

        for blocks_chunk in chunk(block_records, 100):
            for record in blocks_chunk:
                print "Block", record
            self.client.mblock(blocks_chunk)

        if self.must_exist:
            for cidr in current_cidrs:
                if cidr in wanted or cidr + '/32' in wanted:
                    continue
                print "Remove", cidr
                self.client.unblock_now(cidr, "removed from source")
