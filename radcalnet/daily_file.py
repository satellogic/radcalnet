"""
Parse the daily file format.
The main function provided by this module is `read_daily_file`.
However lower-level functions are available for possible reuse in the future.
"""
import datetime as dt


aerosol_types = {'R': '?', 'C': '?', 'D': 'Desert',
                 'M': 'Marine'}


def block_iter(lineiter):
    """
    Iterate over blocks in a file.
    Blocks consist of tab-separated lines, and delimited by empty lines.
    """
    block = []
    for line in lineiter:
        if line.strip() == '':
            if block:
                yield block
            block = []
        else:
            block.append(line.rstrip().split('\t'))

    if block:
        yield block


def parse_metadata_block(block):
    meta = {key.rstrip(':'): val for key, val in block}
    meta['Site'] = meta['Site'].strip()
    assert len(meta['Site']) == 6, 'Invalid site name'
    for float_field in ['Lat', 'Lon', 'Alt']:
        meta[float_field] = float(meta[float_field])
    return meta


# Parsing the data blocks

def read_data_subblock(line_iter, last_header):
    """
    Given an iterator over lines of format ['Header:', 'val1', 'val2'...],
    consume lines until a `last_header` is encountered (inclusive), and
    return the results as a dict
    """
    rows = {}
    for head, *vals in line_iter:
        head = head.rstrip(':')
        rows[head] = vals
        if head == last_header:
            break
    return rows


def read_times_subblock(line_iter):
    rows = read_data_subblock(line_iter, 'Local')
    times = []
    for i, year in enumerate(rows['Year']):
        timestr = '{}_{}_{}'.format(year, rows['DOY(U)'][i], rows['UTC'][i])
        times.append(dt.datetime.strptime(timestr, '%Y_%j_%H:%M'))
    return times


def read_weather_subblock(line_iter):
    rows = read_data_subblock(line_iter, 'Ang')
    for key in ['P', 'T', 'WV', 'O3', 'AOD', 'Ang']:
        rows[key] = [float(val) for val in rows[key]]
    return rows


def read_srf_subblock(line_iter):
    rows = {}
    for head, *vals in line_iter:
        rows[int(head)] = [float(x) for x in vals]
    return rows


def read_types_line(line_iter):
    head, *vals = next(line_iter)
    assert head == 'Type:', 'Unexpected header, ' + head
    for val in vals:
        assert val in aerosol_types, 'Unexpected Aerosol type: ' + val
    return vals


def parse_main_data_block(block):
    lineiter = iter(block)
    times = read_times_subblock(lineiter)
    weather = read_weather_subblock(lineiter)
    weather['Type'] = read_types_line(lineiter)
    srf = read_srf_subblock(lineiter)
    return times, weather, srf


def parse_errors_data_block(block):
    lineiter = iter(block)
    weather_errs = read_weather_subblock(lineiter)
    srf_errs = read_srf_subblock(lineiter)
    return weather_errs, srf_errs


def read_daily_file(f):
    """
    Parse a daily data text file (`.input` or `.output`)
    `f` may be either a file-like object or a local path to such file.
    Results are returned in dicts, with values converted to proper native types
    (int, float, datetime).

    :return: metadata, times, weather, weather_errs, srf, srf_errs
        where `metadata` is a dict of scalar values,
        `times` is a list of datetime objects (representing UTC timestamps),
        and the rest are dicts, whose values are lists with a fixed length
        (`==len(times)`).
    """
    if isinstance(f, str):
        f = open(f, 'rt')
    blockiter = iter(block_iter(f))

    metadata = parse_metadata_block(next(blockiter))
    times, weather, srf = parse_main_data_block(next(blockiter))
    weather_errs, srf_errs = parse_errors_data_block(next(blockiter))
    return metadata, times, weather, weather_errs, srf, srf_errs
