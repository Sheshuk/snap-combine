from .databuffer import DataBlock, DataBuffer
import numpy as np
from hypothesis import given, assume, example, strategies as st
import pytest

time_val = st.floats(-1e10,1e10,allow_nan=False, allow_infinity=False)
times    = st.lists(time_val, min_size=2,max_size=10000, unique=True).map(sorted)

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
    d1 = make_data(1,ts,1)
    d2 = make_data(1,np.array(ts)+(ts[-1]-ts[0]),2)
    d2.ts+=d1.T1()-d1.T0() #shift the time
    buf.put(d1)
    buf.put(d2)
    assert buf.clients == {d1.id: d1+d2}
    assert buf.clients[d1.id].T0() == d1.T0()
    assert buf.clients[d1.id].T1() == d2.T1()
           

