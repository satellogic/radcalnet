import os
import datetime as dt
from radcalnet.data_store import DataStore


proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
store_path = os.path.join(proj_dir, 'tests', 'data', 'datastore')


def test_basic():
    ds = DataStore(store_path)
    ms = ds.get_measuremets('BTCN', dt.datetime(2018, 5, 28, 1, 0), dt.datetime(2018, 5, 28, 2, 0))
    assert len(ms.weather) == 3
    ms = ds.get_measuremets('BTCN', dt.datetime(2018, 5, 28, 4, 0), None)
    assert len(ms.weather) == 7
    ms = ds.get_measuremets('BTCN', None, dt.datetime(2017, 5, 1, 4, 0))
    assert len(ms.weather) == 0
