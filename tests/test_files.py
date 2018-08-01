import os
from radcalnet.daily_file import (
    block_iter, parse_metadata_block, read_daily_file)

proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
store_path = os.path.join(proj_dir, 'tests', 'data', 'datastore')


def test_block_iter():
    path = os.path.join(store_path, 'BTCN', 'BTCN02_2018_148_v00.03.input')
    blocks = list(block_iter(open(path, 'rt')))
    assert len(blocks) == 3
    meta = parse_metadata_block(blocks[0])
    assert meta['Site'] == 'BTCN02'
    assert meta['Lat'] == 40.85486
    assert meta['Lon'] == 109.6272
    assert meta['Alt'] == 1270.0


def test_read_daily_file():
    path = os.path.join(store_path, 'BTCN', 'BTCN02_2018_148_v00.03.input')
    (metadata1, times1,
     weather1, weather1_errs, sr, sr_errs) = read_daily_file(path)
    path = os.path.join(store_path, 'BTCN', 'BTCN02_2018_148_v02.03.output')
    (metadata2, times2,
     weather2, weather2_errs, toa, toa_errs) = read_daily_file(path)
    assert metadata1 == metadata2
    assert times1 == times2
    assert weather1 == weather2
    assert weather1_errs == weather2_errs
    assert len(weather1) == len(weather1_errs)
    assert len(sr) == len(sr_errs)
    assert len(toa) == len(toa_errs)

    assert len(times1) == 13
    for vals in weather1.values():
        assert len(vals) == len(times1)
    for vals in sr.values():
        assert len(vals) == len(times1)
    for vals in toa.values():
        assert len(vals) == len(times1)
