class SourceBlocker:
    must_exist = False

    def __init__(self, client):
        self.client = client
        self.setup()

    @property
    def source(self):
        raise Exception("override source attribute")

    def setup(self):
        pass

    def get_records(self):
        return []

    def run(self):
        wanted = set()
        for record in self.get_records():
            print "Block", record
            self.client.block(**record)
            wanted.add(record['cidr'])

        if self.must_exist:
            for x in self.client.get_expected(self.source):
                if x['cidr'] not in wanted:
                    print "Remove", x
                    self.client.unblock_now(x['cidr'], "removed from source")
