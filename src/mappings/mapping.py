
#todo decide if this will be parent / abstract class and every ledger has to implement it
# or default class (makes sense if mapping is the same for some ledgers)
class Mapping:

    def __init__(self, project_name, dataset):
        self.project_name = project_name
        self.dataset = dataset

    def process(self, timeframe):
        raise NotImplementedError
