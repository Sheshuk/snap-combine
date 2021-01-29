from snap.datablock import DataBlock
import numpy as np
from hypothesis import given, strategies as st
import pytest

time_val = st.floats(-1e10, 1e10, width=32, allow_nan=False, allow_infinity=False)
times =      st.lists(time_val, min_size=2,  max_size=10000, unique=True).map(sorted)
times_long = st.lists(time_val, min_size=10, max_size=10000, unique=True).map(sorted)

def random_DataBlock(ts,**kwargs):
    return DataBlock(ts,zs=np.random.normal(size=len(ts)-1), **kwargs)

@given(ts=times)
def test_limits(ts):
    d = random_DataBlock(ts=ts)
    assert d.T0()==ts[0]
    assert d.T1()==ts[-1]
    assert len(d)==len(ts)-1
    assert len(d)==len(d.zs)


@given(ts=times_long)
def test_add_adjascent(ts):
    #split the list in two
    d1=random_DataBlock(ts)
    d2=random_DataBlock(d1.ts+(ts[-1]-ts[0]))

    d12 = d1+d2
    assert d12.id==d1.id
    assert len(d12)==len(d1)+len(d2)
    assert np.allclose(d12.ts, np.concatenate([d1.ts, d2.ts[1:]]) )
    assert np.allclose(d12.zs, np.concatenate([d1.zs, d2.zs]), equal_nan=True)

@given(ts1=times, ts2=times)
def test_add(ts1, ts2):
    d1=random_DataBlock(ts1)
    d2=random_DataBlock(ts2)

    
    if np.isclose(d1.T1(), d2.T0()):
        d12 = d1+d2
        assert d12.id==d1.id
        assert len(d12)==len(d1)+len(d2)
        assert np.allclose(d12.ts, np.concatenate([d1.ts, d2.ts[1:]]) )
        assert np.allclose(d12.zs, np.concatenate([d1.zs, d2.zs]), equal_nan=True)

    elif d1.T1()<d2.T0():
        d12 = d1+d2
        assert d12.id==d1.id
        assert len(d12)==len(d1)+len(d2)+1
        assert np.allclose(d12.ts, np.concatenate([d1.ts, d2.ts]) )
        assert np.allclose(d12.zs, np.concatenate([d1.zs, [np.nan], d2.zs]), equal_nan=True)

    else:
        with pytest.raises(ValueError, match='Cannot add DataBlocks with d1.T1'):
            d12 = d1+d2

@given(ts=times, p=st.floats(0.0, 1.0, exclude_max=True))
def test_at(ts, p):
    d = random_DataBlock(ts)
    tc = p*d.ts[1:]+(1.-p)*d.ts[:-1]
    assert all(d.find_idx(tc) == np.arange(len(d)))
    assert np.allclose(d.at(tc), d.zs)

@given(ts=times)
def test_at_border(ts):
    d = random_DataBlock(ts)
    assert np.all(d.find_idx(ts) == np.arange(len(d)+1))
    assert np.allclose(d.at(ts[:-1]), d.zs)

@given(ts=times)
def test_at_outside(ts):
    d = random_DataBlock(ts)
    assert np.isnan(d.at(d.T0()-100.))
    assert np.isnan(d.at(d.T1()+100.))

@given(ts=times, t0=time_val)
def test_drop_tail(ts, t0):
    d0 = random_DataBlock(ts)
    d1 = d0.drop_tail(t0)
    if t0<d0.T0():
        assert d1==d0
    else:
        assert d1.T0()==t0
        assert all(d1.ts>=t0)
        assert np.allclose(d1.ts[1:], d0.ts[d0.ts>t0])
        if t0>d0.T1():
            assert len(d1)==0
            assert d1.ts[0]==t0

