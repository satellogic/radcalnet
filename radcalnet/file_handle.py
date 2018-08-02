import os
import re
import datetime as dt

site_info = {
    'RVUS': ('Railroad Valley, United States'),
    'LCFR': ('La Crau, France'),
    'BTCN': ('Baotou, China'),
    'GONA': ('Gobabeb, Namibia')
}


def _re_field(name, fmt):
    return '(?P<{}>{})'.format(name, fmt)


filename_re = re.compile(
    r'{}_{}_{}\.{}'.format(
        *map(_re_field, *zip(*[
            ('instrument', r'[A-Z]{4}\d{2}'),
            ('date', r'\d{4}_\d{3}'),
            ('version', r'v\d{2}\.\d{2}'),
            ('stage', r'input|output')
        ])))
)


class DailyFileHandle:
    """
    Handle for site daily data file
    Contains the path to the file, as well as the parsed metadata that is
    encoded in the filename format.
    """
    date_fmt = '%Y_%j'

    def __init__(self, path):
        self.path = path
        basename = os.path.basename(path)
        parsed = filename_re.match(basename).groupdict()
        self.instrument = parsed['instrument']
        self.site = self.instrument[:4]
        assert self.site in site_info, 'Unrecognized site code: ' + self.site
        self.date = dt.datetime.strptime(parsed['date'], self.date_fmt)
        version = parsed['version']
        assert version[0] == 'v' and version[3] == '.',\
            'Invalid version in filename: ' + version
        self.output_version = version[1:3]
        self.input_version = version[4:6]
        self.stage = parsed['stage']
