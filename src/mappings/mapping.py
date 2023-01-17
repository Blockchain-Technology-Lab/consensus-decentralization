import json

#todo decide if this will be parent / abstract class and every ledger has to implement it
# or default class (makes sense if mapping is the same for some ledgers)
class Mapping:

    def __init__(self, project_name, io_dir):
        self.project_name = project_name
        self.io_dir = io_dir
        self.dataset = None

    def perform_mapping(self, timeframe):
        if self.dataset is None:
            self.dataset = self.read_project_data()
        return self.process(timeframe)

    def read_project_data(self):
        with open(self.io_dir + '/data.json') as f:
            data = json.load(f)
        return data

    def process(self, timeframe):
        raise NotImplementedError
