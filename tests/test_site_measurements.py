import os
import glob
import datetime as dt
import numpy as np
from radcalnet.site_measurements import SiteMeasurements, _process_dailyfile


proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
store_path = os.path.join(proj_dir, 'tests', 'data', 'datastore')


def test_process():
    path = os.path.join(store_path, 'BTCN', 'BTCN02_2018_148_v02.03.output')
    (weather, weather_errs,
     srf, srf_errs, meta) = _process_dailyfile(path)
    assert meta['instrument'] == 'BTCN02'
    assert meta['Alt'] == 1270
    assert len(weather) == 13


def test_basic():
    pathlist = glob.glob(os.path.join(store_path, 'BTCN', '*'))
    # filter by wrong site/instrument
    sm = SiteMeasurements.from_pathlist(pathlist, 'ABCD00')
    assert len(sm.weather) == 0
    # filter by correct site/instrument
    sm = SiteMeasurements.from_pathlist(pathlist, 'BTCN02')
    assert len(sm.weather) == 13
    assert len(sm.toa) == 13
    # without filtering
    sm = SiteMeasurements.from_pathlist(pathlist)
    assert len(sm.sr) == 13
    # validate
    start_time = dt.datetime(2018, 5, 28, 4, 0)
    assert np.max(sm.sr_errs.loc[start_time:, :1000].values) < 0.02
    assert np.min(sm.sr_errs.loc[start_time:, :1000].values) > 0
    assert np.max(sm.toa_errs.loc[start_time:, :1000].values) < 0.02
    assert np.min(sm.toa_errs.loc[start_time:, :1000].values) > 0
    avg_sr = np.average(sm.sr.loc[start_time:, :1000].values, axis=0)
    assert np.all(avg_sr < 1.0)
    avg_toa = np.average(sm.toa.loc[start_time:, :1000].values, axis=0)
    assert np.all(avg_toa < 1.0)
    # for high enough wavelength, toa is smaller than sr
    assert np.all((avg_toa < avg_sr)[-30:])
