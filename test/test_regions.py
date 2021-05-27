import asyncio
from snap.elements.combine.regions import RegionsQueue
from hypothesis import given, assume, example, strategies as st
import numpy as np
import pytest

time_val = st.floats(-1e10,1e10,width=32,allow_nan=False, allow_infinity=False)
times =    st.lists(time_val, min_size=2,max_size=10000, unique=True).map(sorted)
region =   st.tuples(time_val,time_val).map(sorted)

@pytest.mark.asyncio
async def test_timeout_on_pop_empty_queue():
    rq = RegionsQueue()
    assert rq.regions == []
    with pytest.raises(asyncio.exceptions.TimeoutError):
        res = await asyncio.wait_for(rq.get(), 1)

@pytest.mark.asyncio
@given(r=region.map(sorted))
async def test_put_pop_same_region(r):
    rq = RegionsQueue()
    await rq.put(*r)
    assert np.allclose(rq.regions, [r])
    res = await rq.get()
    assert np.allclose(res, r)
    assert rq.regions == []

@pytest.mark.asyncio
@given(ts = times)
async def test_merge(ts):
    rq = RegionsQueue()
    
    t0s = ts[:-1]
    t1s = ts[1:]
    for t0,t1 in zip(t0s,t1s):
        await rq.put(t0,t1)

    res = await rq.get()
    assert np.allclose(res, (ts[0],ts[-1]) )
    assert rq.regions == []

def do_collide(r1,r2):
    return (r1[0]<=r2[1]) & (r2[0]<=r1[1])

@pytest.mark.asyncio
@given(region, region)
async def test_random_regions(r0,r1):
    rq = RegionsQueue()
    
    await rq.put(*r0)
    await rq.put(*r1)
    
    res = await rq.get()

    if do_collide(r0,r1): #regions are merged
        assert rq.regions == []
        assert np.allclose(res,[min(r0[0],r1[0]),max(r1[1],r0[1])] )
    else: #regions are separate
        assert np.allclose(res, r0)
        assert len(rq.regions)==1
        res = await rq.get()
        assert np.allclose(res, r1)

