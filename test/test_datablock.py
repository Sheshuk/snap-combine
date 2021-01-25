from snap.datablock import DataBlock
import numpy as np
from hypothesis import given, assume, strategies as st
import pytest

d1 = DataBlock(ts=[0.,1.,2.], zs=[1.,2.], id=1)
d2 = DataBlock(ts=[2.,3.,4.], zs=[3.,4.], id=1)
d3 = DataBlock(ts=[5.,6.,7.], zs=[5.,6.], id=1)


time_val = st.floats(allow_nan=False)
times =      st.lists(time_val, min_size=2,max_size=10000, unique=True).map(sorted)
times_long = st.lists(time_val, min_size=10,max_size=10000, unique=True).map(sorted)

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
    d1=random_DataBlock(ts[:6])
    d2=random_DataBlock(ts[5:])

    d12 = d1+d2
    assert np.allclose(d12.ts, ts)
    assert np.allclose(d12.zs, np.append(d1.zs, d2.zs))
    assert d12.id==d1.id
    assert len(d12)==len(ts)-1

@given(ts1=times, ts2=times)
def test_add(ts1,ts2):
    d1=random_DataBlock(ts1)
    d2=random_DataBlock(ts2)

    if d1.T1()>d2.T0():
        with pytest.raises(ValueError, match='Cannot add DataBlocks with d1.T1'):
            d12 = d1+d2

    elif d1.T1()==d2.T0():
        d12 = d1+d2
        assert d12.id==d1.id
        assert len(d12)==len(d1)+len(d2)
        assert np.allclose(d12.ts, np.concatenate([d1.ts,d2.ts[1:]]) )
        assert np.allclose(d12.zs, np.concatenate([d1.zs,d2.zs]), equal_nan=True)

    else:
        d12 = d1+d2
        assert d12.id==d1.id
        assert len(d12)==len(d1)+len(d2)+1
        assert np.allclose(d12.ts, np.concatenate([d1.ts,d2.ts]) )
        assert np.allclose(d12.zs, np.concatenate([d1.zs,[np.nan],d2.zs]), equal_nan=True)

@given(ts=times)
def test_slice_full(ts):
    d = random_DataBlock(ts)
    assert d.slice(-np.inf,np.inf) == d
    assert d.slice(ts[0],ts[-1]) == d

@given(ts=times, t0=time_val, t1=time_val)
def test_slice_inside(ts,t0,t1):
    d = random_DataBlock(ts)
    ds = d.slice(t0,t1)
   
    assert ds.T0()==max(t0,d.T0())
    assert ds.T1()==min(t1,d.T1())
    
    idx_sel = (d.ts>=t0)&(d.ts<=t1)
    assert ds.zs == d.zs[idx_sel]


