from snap.elements.combine.databuffer import DataBlock, DataBuffer
import numpy as np
from hypothesis import given, strategies as st
import pytest

time_val = st.floats(-1e10, 1e10, allow_nan=False, allow_infinity=False)
times    = st.lists(time_val, min_size=2, max_size=10000, unique=True).map(sorted)

def make_data(id,ts,z=0):
    return DataBlock(id=id, ts=ts, zs=[z]*(len(ts)-1))

@given(ts=times)
def test_new_clients(ts):
    buf = DataBuffer()
    d1 = make_data(1,ts)
    d2 = make_data(2,ts)
    buf.put(d1)
    assert buf.clients == {d1.id: d1}
    buf.put(d2)
    assert buf.clients == {d.id: d for d in [d1,d2]}
    with pytest.raises(ValueError):
        buf.put(d2)
           
@given(ts=times)
def test_append_data(ts):
    buf = DataBuffer()
    d1 = make_data(1,ts)
    d2 = make_data(1,np.array(ts)+(ts[-1]-ts[0]))
    d2.ts+=d1.T1()-d1.T0() #shift the time
    buf.put(d1)
    buf.put(d2)
    assert buf.clients == {d1.id: d1+d2}

@given(ts1=times, ts2=times, tget=times)
def test_at(ts1,ts2,tget):
    buf = DataBuffer()
    d1 = make_data(1,ts1)
    d2 = make_data(2,ts2)
    buf.put(d1)
    buf.put(d2)
    res = buf.at(tget)
    assert res.shape==(len(tget),2)
    assert len(res)==len(tget)
    assert np.allclose( buf.at(tget).T, [d1.at(tget), d2.at(tget)], equal_nan=True)

@given(ts1=times,ts2=times,t0=time_val, t1=time_val)
def test_slice_ts(ts1,ts2,t0,t1):
    buf = DataBuffer()
    d1 = make_data(1,ts1)
    d2 = make_data(2,ts2)
    buf.put(d1)
    buf.put(d2)
    tslice = buf.slice_ts(t0,t1)
    for d in [d1,d2]:
        assert all(np.isin(d.ts[(d.ts>t0) & (d.ts<t1)],tslice))
    assert all(np.isin([t0,t1],tslice))



