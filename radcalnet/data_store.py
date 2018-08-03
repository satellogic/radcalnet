import os
import numpy as np
from .file_handle import DailyFileHandle
from .site_measurements import SiteMeasurements


class DayfileIndex:
    def __init__(self, path):
        self.path = path
        handles = [DailyFileHandle(os.path.join(path, fname))
                   for fname in os.listdir(path)]
        self.handles = sorted(handles, key=lambda x: x.date)
        self.datestamps = np.array(
            [np.datetime64(x.date.date()) for x in self.handles])

    def __getitem__(self, key):
        assert isinstance(key, slice)
        assert key.step is None
        start = (np.datetime64(key.start.date()) if key.start is not None
                 else self.datestamps[0] - np.timedelta64(1, 'D'))
        stop = (np.datetime64(key.stop.date()) if key.stop is not None
                else self.datestamps[-1] + np.timedelta64(1, 'D'))
        sind = np.searchsorted(self.datestamps, start, side='left')
        eind = np.searchsorted(self.datestamps, stop, side='right')
        return [handle.path for handle in self.handles[sind:eind]]


class DataStore:
    def __init__(self, path):
        self.path = path
        self._build_index()

    def _build_index(self):
        self.site_dirs = {
            name: os.path.join(self.path, name)
            for name in os.listdir(self.path)
        }
        self.site_index = {
            name: DayfileIndex(path)
            for name, path in self.site_dirs.items()
        }

    def get_measuremets(self, site, fromtime=None, totime=None):
        paths = self.site_index[site][fromtime:totime]
        sm = SiteMeasurements.from_pathlist(paths)
        return sm[fromtime:totime]
