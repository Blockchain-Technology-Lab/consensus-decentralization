import logging
from collections import defaultdict
from dateutil.rrule import rrule, MONTHLY, WEEKLY, YEARLY, DAILY
import datetime
import consensus_decentralization.helper as hlp


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
        :param data_to_aggregate: list of dictionaries. The data that will be aggregated
        """
        self.project = project
        self.data_to_aggregate = sorted(data_to_aggregate, key=lambda x: x['timestamp'])
        self.data_start_date = hlp.get_timeframe_beginning(self.data_to_aggregate[0]['timestamp'][:10])
        self.data_end_date = hlp.get_timeframe_beginning(self.data_to_aggregate[-1]['timestamp'][:10])
        self.aggregated_data_dir = io_dir / 'blocks_per_entity'
        self.aggregated_data_dir.mkdir(parents=True, exist_ok=True)

        self.monthly_data_breaking_points = [(self.data_start_date.strftime('%Y-%m'), 0)]
        for idx, block in enumerate(self.data_to_aggregate):
            if block['timestamp'][:7] != self.monthly_data_breaking_points[-1][0]:
                self.monthly_data_breaking_points.append((block['timestamp'][:7], idx))

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
            for month, month_block_index in self.monthly_data_breaking_points:
                start_index = 0
                if timeframe_start >= hlp.get_timeframe_beginning(month):
                    start_index = max(month_block_index - 1, 0)
                    break
            for block in self.data_to_aggregate[start_index:]:
                block_timestamp = hlp.get_timeframe_beginning(block['timestamp'][:10])
                if timeframe_end < block_timestamp:
                    break
                if timeframe_start <= block_timestamp <= timeframe_end:
                    blocks_per_entity[block['creator']] += 1

        return blocks_per_entity


def divide_timeframe(timeframe, granularity):
    """
    Divides the timeframe into smaller timeframes of the given granularity
    :param timeframe: a tuple of (start_date, end_date) where each date is a datetime.date object.
    :param granularity: the granularity that will be used for the analysis. It can be one of: day, week, month, year, all
    :return: a list of tuples of (start_date, end_date) where each date is a datetime.date object and each tuple
        corresponds to a timeframe of the given granularity
    :raises ValueError: if the timeframe is not valid (i.e. end date preceeds start_date) or if the granularity is not
        one of: day, week, month, year
    """
    timeframe_start, timeframe_end = timeframe
    if timeframe_end < timeframe_start:
        raise ValueError(f'Invalid timeframe: {timeframe}')
    if granularity == 'day':
        start_dates = [dt.date() for dt in rrule(freq=DAILY, dtstart=timeframe_start, until=timeframe_end)]
        end_dates = start_dates
    elif granularity == 'week':
        start_dates = [dt.date() for dt in rrule(freq=WEEKLY, dtstart=timeframe_start, until=timeframe_end)]
        end_dates = [dt - datetime.timedelta(days=1) for dt in start_dates[1:]] + [timeframe_end]
    elif granularity == 'month':
        start_dates = [dt.date() for dt in rrule(freq=MONTHLY, dtstart=timeframe_start.replace(day=1), until=timeframe_end)]
        start_dates[0] = timeframe_start
        end_dates = [dt - datetime.timedelta(days=1) for dt in start_dates[1:]] + [timeframe_end]
    elif granularity == 'year':
        start_dates = [dt.date() for dt in rrule(freq=YEARLY, dtstart=timeframe_start.replace(month=1, day=1), until=timeframe_end)]
        start_dates[0] = timeframe_start
        end_dates = [dt - datetime.timedelta(days=1) for dt in start_dates[1:]] + [timeframe_end]
    else:
        # no need to divide the timeframe
        start_dates = [timeframe_start]
        end_dates = [timeframe_end]
    return list(zip(start_dates, end_dates))


def aggregate(project, output_dir, timeframe, aggregate_by, force_aggregate, mapped_data=None):
    """
    Aggregates the results of the mapping process for the given project and timeframe. The results are saved in a csv
    file in the project's output directory. Note that the output file is created (just with the headers) even if there
    is no data to aggregate.
    :param project: the name of the project
    :param output_dir: the path to the general output directory
    :param timeframe: a tuple of (start_date, end_date) where each date is a datetime.date object
    :param aggregate_by: the granularity that will be used for the analysis. It can be one of: day, week, month,
        year, all
    :param force_aggregate: bool. If True, then the aggregation will be performed, regardless of whether aggregated
        data for the project and specified granularity already exist
    :param mapped_data: list of dictionaries (the data that will be aggregated). If None, then the data will be read
    from the project's output directory
    :returns: a list of strings that correspond to the time chunks of the aggregation or None if no aggregation took
    place (the corresponding output file already existed and force_aggregate was set to False)
    """
    project_io_dir = output_dir / project
    if mapped_data is None:
        mapped_data = hlp.read_mapped_project_data(project_io_dir)
    aggregator = Aggregator(project, project_io_dir, mapped_data)

    filename = hlp.get_blocks_per_entity_filename(aggregate_by=aggregate_by, timeframe=timeframe)
    output_file = aggregator.aggregated_data_dir / filename

    if not output_file.is_file() or force_aggregate:
        logging.info(f'Aggregating {project} data..')
        timeframe_chunks = divide_timeframe(timeframe=timeframe, granularity=aggregate_by)
        blocks_per_entity = defaultdict(lambda: [0] * len(timeframe_chunks))
        for i, chunk in enumerate(timeframe_chunks):
            chunk_start, chunk_end = chunk
            chunk_blocks_per_entity = aggregator.aggregate(chunk_start, chunk_end)
            for entity, blocks in chunk_blocks_per_entity.items():
                blocks_per_entity[entity][i] = blocks

        timeframe_chunks = hlp.format_time_chunks(time_chunks=timeframe_chunks, granularity=aggregate_by)
        hlp.write_blocks_per_entity_to_file(
            output_dir=aggregator.aggregated_data_dir,
            blocks_per_entity=blocks_per_entity,
            time_chunks=timeframe_chunks,
            filename=filename
        )
        return timeframe_chunks
    return None
