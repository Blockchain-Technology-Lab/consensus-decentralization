import logging
from collections import defaultdict
import datetime
import consensus_decentralization.helper as hlp


class Aggregator:
    """
    Class used to aggregate the results of the mapping process.  Reads a json file that is the output of the mapping
    and aggregates the results for a given timeframe (e.g. month) by counting the number of blocks produced by
    each entity. The result is a dictionary of entities that produced blocks in the given timeframe and the number of
    blocks they produced
    """

    def __init__(self, project, io_dir, mapped_data=None):
        """
        :param project: str. Name of the project
        :param io_dir: Path. Path to the project's output directory
        """
        self.project = project
        self.data_to_aggregate = hlp.read_mapped_project_data(io_dir) if mapped_data is None else mapped_data
        self.data_start_date = hlp.get_timeframe_beginning(hlp.get_date_from_block(self.data_to_aggregate[0]))
        self.data_end_date = hlp.get_timeframe_beginning(hlp.get_date_from_block(self.data_to_aggregate[-1]))
        self.aggregated_data_dir = io_dir / hlp.get_aggregated_data_dir_name(hlp.get_clustering_flag())
        self.aggregated_data_dir.mkdir(parents=True, exist_ok=True)

        self.monthly_data_breaking_points = [(self.data_start_date.strftime('%Y-%m'), 0)]
        for idx, block in enumerate(self.data_to_aggregate):
            block_month = hlp.get_date_from_block(block, level='month')
            if block_month != self.monthly_data_breaking_points[-1][0]:
                self.monthly_data_breaking_points.append((block_month, idx))

    def aggregate(self, timeframe_start, timeframe_end):
        """
        Processes the mapped data to aggregate the results for the given timeframe
        :param timeframe_start: datetime.date object. The date to start aggregating from
        :param timeframe_end: datetime.date object. The date to stop aggregating at
        :returns: a dictionary with the entities and the number of blocks they have produced in the period between
        timeframe_start and timeframe_end (inclusive)
        """
        blocks_per_entity = defaultdict(int)
        if self.data_start_date <= timeframe_end and self.data_end_date >= timeframe_start:
            start_index = 0
            for month, month_block_index in self.monthly_data_breaking_points:
                if timeframe_start >= hlp.get_timeframe_beginning(month):
                    start_index = max(month_block_index - 1, 0)
                    break
            for block in self.data_to_aggregate[start_index:]:
                block_timestamp = hlp.get_timeframe_beginning(hlp.get_date_from_block(block))
                if timeframe_start <= block_timestamp <= timeframe_end:
                    blocks_per_entity[block['creator']] += 1
                elif timeframe_end < block_timestamp:
                    break

        return blocks_per_entity


def divide_timeframe(timeframe, estimation_window, frequency):
    """
    Divides the timeframe into smaller timeframes based on the given estimation_window and frequency. Each smaller
    timeframe will be estimation_window days long and the start (or end) date of each smaller timeframe will be
    frequency days apart from the start (or end) date of the previous timeframe. The last timeframe will not
    necessarily have the end date of the original timeframe, it might be some days before that, so  that all time
    frames produced have equal length.
    If the estimation_window is None, then the timeframe is not divided and the list will contain only one
    tuple with the start and end dates of the timeframe. If the frequency is None, then the list will contain only one
    tuple with the start and end dates of the timeframe.
    :param timeframe: a tuple of (start_date, end_date) where each date is a datetime.date object.
    :param estimation_window: int or None. The number of days to include in each time chunk. If None, the entire
        timeframe will be considered as one chunk.
    :param frequency: int or None. The number of days between each sample start date. If None, only one sample will be
        considered, spanning the entire timeframe (i.e. it needs to be combined with None estimation_window).
    :returns: a list of tuples of (start_date, end_date) where each date is a datetime.date object. If the estimation
    window is larger than the timeframe, then an empty list is returned.
    :raises ValueError: if the timeframe is not valid (i.e. end date preceeds start_date)
    """
    timeframe_start, timeframe_end = timeframe
    if timeframe_end < timeframe_start:
        raise ValueError(f'Invalid timeframe: {timeframe}')
    if estimation_window is None:
        return [(timeframe_start, timeframe_end)]
    time_chunks = []
    first_window_day = timeframe_start
    last_window_day = timeframe_start + datetime.timedelta(days=estimation_window - 1)
    while last_window_day <= timeframe_end:
        time_chunks.append((first_window_day, last_window_day))
        first_window_day += datetime.timedelta(days=frequency)
        last_window_day += datetime.timedelta(days=frequency)
    return time_chunks


def aggregate(project, output_dir, timeframe, estimation_window, frequency, force_aggregate, mapped_data=None):
    """
    Aggregates the results of the mapping process for the given project and timeframe. The results are saved in a csv
    file in the project's output directory. Note that the output file is created (just with the headers) even if there
    is no data to aggregate.
    :param project: the name of the project
    :param output_dir: the path to the general output directory
    :param timeframe: a tuple of (start_date, end_date) where each date is a datetime.date object
    :param estimation_window: int or None. The number of days to use for aggregating the data (i.e. counting all the
        blocks produced by the entity within estimation_window days). If None, the entire timeframe will be considered
        as one chunk.
    :param frequency: int or None. The number of days to consider for the frequency of the analysis (i.e. the number
        of days between each data point considered in the analysis). If None, only one data point will be considered,
        spanning the entire timeframe (i.e. it needs to be combined with None estimation_window).
    :param force_aggregate: bool. If True, then the aggregation will be performed, regardless of whether aggregated
        data for the project and specified window / frequency already exist
    :returns: a list of strings that correspond to the time chunks of the aggregation or None if no aggregation took
    place (the corresponding output file already existed and force_aggregate was set to False)
    """
    if estimation_window is not None:
        if timeframe[0] + datetime.timedelta(days=estimation_window - 1) > timeframe[1]:
            raise ValueError('The estimation window is too large for the given timeframe')

    project_io_dir = output_dir / project
    aggregator = Aggregator(project, project_io_dir, mapped_data=mapped_data)

    filename = hlp.get_blocks_per_entity_filename(timeframe=timeframe, estimation_window=estimation_window, frequency=frequency)
    output_file = aggregator.aggregated_data_dir / filename

    if not output_file.is_file() or force_aggregate:
        logging.info(f'Aggregating {project} data..')
        timeframe_chunks = divide_timeframe(timeframe=timeframe, estimation_window=estimation_window, frequency=frequency)
        representative_dates = hlp.get_representative_dates(time_chunks=timeframe_chunks)
        blocks_per_entity = defaultdict(dict)
        for i, chunk in enumerate(timeframe_chunks):
            chunk_start, chunk_end = chunk
            chunk_blocks_per_entity = aggregator.aggregate(chunk_start, chunk_end)
            for entity, blocks in chunk_blocks_per_entity.items():
                blocks_per_entity[entity][representative_dates[i]] = blocks

        hlp.write_blocks_per_entity_to_file(
            output_dir=aggregator.aggregated_data_dir,
            blocks_per_entity=blocks_per_entity,
            dates=representative_dates,
            filename=filename
        )
        return timeframe_chunks
    return None
