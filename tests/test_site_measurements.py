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


def test_ops():
    pathlist = glob.glob(os.path.join(store_path, 'BTCN', '*'))
    sm = SiteMeasurements.from_pathlist(pathlist)
    start_time = dt.datetime(2018, 5, 28, 4, 0)
    end_time = dt.datetime(2018, 5, 28, 7, 0)
    # Test slicing
    sm1 = sm[start_time:]
    assert len(sm1.weather) == 7
    assert np.all(sm.weather['T'][start_time:] == sm1.weather['T'])
    assert np.all(sm.toa[start_time:].loc[:, 500:700].values == sm1.toa.loc[:, 500:700].values)

    sm2 = sm1[end_time + dt.timedelta(seconds=1):]
    assert len(sm2.weather) == 0
    sm2 = sm1[:start_time - dt.timedelta(seconds=1)]
    assert len(sm2.weather) == 0
    sm2 = sm1[start_time - dt.timedelta(seconds=1):end_time + dt.timedelta(minutes=3)]
    assert len(sm2.weather) == 7

    # Test merging
    cut_time = start_time + dt.timedelta(hours=2.1212)
    sm2 = sm1[:cut_time]
    sm3 = sm1[cut_time:]
    assert np.all((sm2 + sm3).weather['WV'].values == sm1.weather['WV'].values)
    # now with overlap
    sm2 = sm1[:cut_time + dt.timedelta(hours=2)]
    sm3 = sm1[cut_time:]
    assert np.all((sm2 + sm3).weather['T'].values == sm1.weather['T'].values)


def test_plot():
    pathlist = glob.glob(os.path.join(store_path, 'BTCN', '*'))
    sm = SiteMeasurements.from_pathlist(pathlist)[dt.datetime(2018, 5, 28):dt.datetime(2018, 5, 29)]

    # try various types of plots, make sure none fails:
    for with_errors in [False, True]:
        for measurements in ['toa', 'O3', ['O3', 'T']]:
            spectrum = range(400, 430) if 'toa'in measurements else None
            sm.plot(measurements, spectrum, with_errors=with_errors, show=False)
