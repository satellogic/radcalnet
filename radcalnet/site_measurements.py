import itertools
import numpy as np
import pandas as pd
from .daily_file import read_daily_file
from .file_handle import DailyFileHandle


_srf_range = list(range(400, 2500+1, 10))
_table_columns = dict(
    weather=['P', 'T', 'WV', 'O3', 'AOD', 'Ang', 'Type'],
    weather_errs=['P', 'T', 'WV', 'O3', 'AOD', 'Ang'],
    sr=_srf_range, sr_errs=_srf_range,
    toa=_srf_range, toa_errs=_srf_range
)


def _dataframe_merge(df1, df2):
    """
    Merge two dataframes (with same columns) by index.
    """
    return df1.merge(df2, how='outer', on=list(df2.columns), left_index=True, right_index=True)


def _filehandle_key(handle):
    return handle.instrument, handle.date.date()


def _meta_coords(meta):
    return tuple(meta[key] for key in ['Lon', 'Lat', 'Alt'])


def _process_dailyfile(path, meta=None):
    """
    Do some validation and conversions on data read from file.
    Update the site coordinates in `meta` if not already done.
    :return: weather, weather_errs, srf, srf_errs, `meta`
    """
    (file_meta, times,
     weather, weather_errs, srf, srf_errs) = read_daily_file(path)
    if meta is None:
        meta = {'instrument': file_meta['Site']}
    assert file_meta['Site'] == meta['instrument'], 'File metadata not matching expected data'

    coords = tuple(meta.setdefault(key, file_meta[key]) for key in ['Lon', 'Lat', 'Alt'])
    assert _meta_coords(file_meta) == coords, 'Site coordinates not matching other files'

    weather = pd.DataFrame(weather, index=times)
    weather_errs = pd.DataFrame(weather_errs, index=times)
    # Note: take care to skip the non-numeric 'Type' (Aerosol type) column
    # (which is not available in the weather_errs data)
    for col in weather_errs.columns:
        weather.loc[weather[col] >= 9000, col] = np.nan
        weather_errs.loc[weather_errs[col] >= 9000, col] = np.nan

    srf = pd.DataFrame(srf, index=times)
    srf[srf >= 9000] = np.nan
    srf_errs = pd.DataFrame(srf_errs, index=times)
    srf_errs[srf_errs >= 9000] = np.nan
    return weather, weather_errs, srf, srf_errs, meta


class SiteMeasurements:
    def __init__(self, weather, weather_errs, sr, sr_errs, toa, toa_errs, meta):
        self.weather, self.weather_errs = weather, weather_errs
        self.sr, self.sr_errs = sr, sr_errs
        self.toa, self.toa_errs = toa, toa_errs
        self.meta = meta

    @classmethod
    def from_pathlist(cls, paths, instrument=None):
        """
        Build measurements from a list of filename.
        Filenames are filtered to match a uniform site/instrument.
        (if not specified, site is taken from the first filename).
        """
        assert len(paths) > 0, 'Must specify at least one data file'
        if (instrument is not None):
            meta = dict(site=instrument[:4], instrument=instrument)
        else:
            handle = DailyFileHandle(paths[0])
            meta = dict(
                site=handle.site,
                instrument=handle.instrument
            )

        filehandles = map(DailyFileHandle, sorted(paths))
        data = {key: pd.DataFrame([], columns=_table_columns[key])
                for key in _table_columns.keys()}
        for key, handles in itertools.groupby(filehandles, _filehandle_key):
            if key[0] != meta['instrument']:
                continue

            handles = list(handles)
            assert len(handles) in {1,2}, 'Duplicate input files?'

            for handle in handles:
                weather, weather_errs, srf, srf_errs, _meta = _process_dailyfile(handle.path, meta)
                for key in ['weather', 'weather_errs']:
                    data[key] = _dataframe_merge(data[key], locals()[key])

                names = {
                    'input': ['sr', 'sr_errs'],
                    'output': ['toa', 'toa_errs']
                }[handle.stage]
                for i, df in enumerate([srf, srf_errs]):
                    data[names[i]] = _dataframe_merge(data[names[i]], df)
            # end loop on the two handles
        # end loop on file-pairs
        return cls(data['weather'], data['weather_errs'],
                   data['sr'], data['sr_errs'], data['toa'], data['toa_errs'],
                   meta)
