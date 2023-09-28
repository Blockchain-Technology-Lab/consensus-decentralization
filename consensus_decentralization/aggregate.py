import argparse
import logging
from collections import defaultdict
import consensus_decentralization.helper as hlp
from consensus_decentralization.map import ledger_mapping


class Aggregator:
    """
    Class used to aggregate the results of the mapping process.  Reads a json file that is the output of the mapping
    and aggregates the results for a given timeframe (e.g. month) by counting the number of blocks produced by
    each entity. The result is a dictionary of entities that produced blocks in the given timeframe and the number of
    blocks they produced
    """

    def __init__(self, project, io_dir, data_to_aggregate):
        """
        :param project: str. Name of the project
        :param io_dir: Path. Path to the project's output directory
        """
        self.project = project
        self.data_to_aggregate = data_to_aggregate
        self.aggregated_data_dir = io_dir / 'blocks_per_entity'
        self.aggregated_data_dir.mkdir(parents=True, exist_ok=True)

    def aggregate(self, timeframe_start, timeframe_end):
        """
        Processes the mapped data to aggregate the results for the given timeframe
        :param timeframe_start: datetime.date object. The date to start aggregating from
        :param timeframe_end: datetime.date object. The date to stop aggregating at
        :returns: a dictionary with the entities and the number of blocks they have produced in the period between
        timeframe_start and timeframe_end (inclusive)
        """
        timeframe_blocks = [block for block in self.data_to_aggregate
                            if timeframe_start <= hlp.get_timeframe_beginning(block['timestamp'][:10]) <= timeframe_end]
        blocks_per_entity = defaultdict(int)
        for block in timeframe_blocks:
            blocks_per_entity[block['creator']] += 1

        filename = f'from_{timeframe_start}_to_{timeframe_end}'
        if len(blocks_per_entity) > 0:
            hlp.write_blocks_per_entity_to_file(output_dir=self.aggregated_data_dir,
                                                blocks_per_entity=blocks_per_entity, filename=filename)
        return blocks_per_entity


def aggregate(project, output_dir, timeframes, force_aggregate, mapped_data=None):
    logging.info(f'Aggregating {project} data..')
    project_io_dir = output_dir / project
    if mapped_data is None:
        mapped_data = hlp.read_mapped_project_data(project_io_dir)
    aggregator = Aggregator(project, project_io_dir, mapped_data)

    years_done = set()  # Keep track of computed yearly aggregations to avoid recomputing them in the same run
    for timeframe in timeframes:
        timeframe_start = hlp.get_timeframe_beginning(timeframe)
        timeframe_end = hlp.get_timeframe_end(timeframe)
        output_file = aggregator.aggregated_data_dir / f'from_{timeframe_start}_to_{timeframe_end}.csv'
        if not output_file.is_file() or force_aggregate:
            aggregator.aggregate(timeframe_start, timeframe_end)

            # Get mapped data for the year that corresponds to the timeframe.
            # This is needed because the Gini coefficient is computed over all entities per each year.
            year = timeframe[:4]
            year_start = hlp.get_timeframe_beginning(year)
            year_end = hlp.get_timeframe_end(year)
            year_file = aggregator.aggregated_data_dir / f'from_{year_start}_to_{year_end}.csv'
            if not year_file.is_file() or (force_aggregate and year not in years_done):
                aggregator.aggregate(year_start, year_end)
                years_done.add(year)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=None,
        choices=[ledger for ledger in ledger_mapping],
        help='The ledgers that will be analyzed.'
    )
    parser.add_argument(
        '--timeframe',
        nargs="?",
        type=hlp.valid_date,
        default=None,
        help='The timeframe that will be analyzed.'
    )
    args = parser.parse_args()

    start_date, end_date = hlp.get_start_end_dates()

    timeframe = args.timeframe
    if timeframe:
        timeframes = [timeframe]
    else:
        timeframes = []
        for year in range(start_date, end_date + 1):
            for month in range(1, 13):
                timeframes.append(f'{year}-{str(month).zfill(2)}')

    for ledger in args.ledgers:
        aggregate(ledger, hlp.OUTPUT_DIR, timeframes, force_aggregate=False)
