import json


class Mapping:
    """
    Base class for a mapping. All mapping classes need to inherit from this class.

    :ivar project_name: the name of the project associated with a specific mapping instance
    :ivar io_dir: the directory that includes the parsed data related to the project
    :ivar dataset: a dictionary with the parsed data of the project
    """

    def __init__(self, project_name, io_dir):
        self.project_name = project_name
        self.io_dir = io_dir
        self.dataset = None

    def perform_mapping(self, timeframe):
        """
        Makes sure that the parsed data are loaded into the instance and calls process to perform the mapping
        :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
        format)
        :returns: a dictionary with the entities and the number of blocks they have produced over the given timeframe
        """
        if self.dataset is None:
            self.dataset = self.read_project_data()
        return self.process(timeframe)

    def read_project_data(self):
        """
        Reads the parsed data from the directory specified by the instance
        :returns: a dictionary with the parsed data
        """
        with open(self.io_dir / 'parsed_data.json') as f:
            data = json.load(f)
        return data

    def process(self, timeframe):
        """
        Processes the parsed data and outputs the mapped data.
        Has to be implemented by child classes.
        :param timeframe: string that corresponds to the timeframe under consideration (in YYYY-MM-DD, YYYY-MM or YYYY
        format)
        """
        raise NotImplementedError

