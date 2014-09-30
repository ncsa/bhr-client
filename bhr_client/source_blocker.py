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
        return []

    def run(self):
        wanted = set()
        current = self.client.get_expected(self.source)
        current_cidrs = set(x['cidr'] for x in current)
        for record in self.get_records():
            cidr = record['cidr']
            if '/' not in cidr:
                cidr += '/32'
            wanted.add(cidr)
            if cidr in current_cidrs:
                continue
            print "Block", record
            record['source'] = self.source
            record['duration'] = self.duration
            self.client.block(**record)

        if self.must_exist:
            for cidr in current_cidrs:
                if cidr in wanted or cidr + '/32' in wanted:
                    continue
                print "Remove", x
                self.client.unblock_now(cidr, "removed from source")
