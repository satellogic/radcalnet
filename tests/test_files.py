import os
from radcalnet.daily_file import (
    block_iter, parse_metadata_block, read_daily_file)
from radcalnet.file_handle import DailyFileHandle


proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
store_path = os.path.join(proj_dir, 'tests', 'data', 'datastore')
inputfile_path = os.path.join(
    store_path, 'BTCN', 'BTCN02_2018_148_v00.03.input')
outputfile_path = os.path.join(
    store_path, 'BTCN', 'BTCN02_2018_148_v02.03.output')


def test_block_iter():
    path = os.path.join(store_path, 'BTCN', 'BTCN02_2018_148_v00.03.input')
    blocks = list(block_iter(open(path, 'rt')))
    assert len(blocks) == 3
    meta = parse_metadata_block(blocks[0])
    assert meta['Site'] == 'BTCN02'
    assert meta['Lat'] == 40.85486
    assert meta['Lon'] == 109.6272
    assert meta['Alt'] == 1270.0


def test_daily_file():
    inputfile = DailyFileHandle(inputfile_path)
    assert os.path.isfile(inputfile.path)
    assert inputfile.site == 'BTCN'
    assert inputfile.stage == 'input'
    outputfile = DailyFileHandle(outputfile_path)
    assert os.path.isfile(outputfile.path)
    assert outputfile.stage == 'output'
    assert (inputfile.instrument, inputfile.date) == (outputfile.instrument, outputfile.date)


def test_read_daily_file():
    inputfile = DailyFileHandle(inputfile_path)
    (metadata1, times1,
     weather1, weather1_errs, sr, sr_errs) = read_daily_file(inputfile_path)
    assert times1[0].date() == inputfile.date.date()
    assert metadata1['Site'] == inputfile.instrument
    assert 'Type' in weather1
    assert set(weather1.keys()) - {'Type'} == set(weather1_errs.keys())

    (metadata2, times2,
     weather2, weather2_errs, toa, toa_errs) = read_daily_file(outputfile_path)
    assert metadata1 == metadata2
    assert times1 == times2
    assert weather1 == weather2
    assert weather1_errs == weather2_errs
    assert len(weather1) == len(weather1_errs) + 1
    assert len(sr) == len(sr_errs)
    assert len(toa) == len(toa_errs)

    assert len(times1) == 13
    for vals in weather1.values():
        assert len(vals) == len(times1)
    for vals in sr.values():
        assert len(vals) == len(times1)
    for vals in toa.values():
        assert len(vals) == len(times1)
