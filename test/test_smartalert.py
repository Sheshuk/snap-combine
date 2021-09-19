import asyncio
from snap.datablock import DataBlock
from snap.elements.process import SmartAlert
import numpy as np
import pytest

async def no_more(obj, timeout=1):
    with pytest.raises(asyncio.TimeoutError):
        res = await asyncio.wait_for(obj.get(),timeout=timeout)

async def get(obj, timeout=1):
    res = await asyncio.wait_for(obj.get(),timeout=timeout)
    return res

@pytest.mark.asyncio
async def test_below_threshold_yields_no_alerts():
    sa = SmartAlert(threshold=5, timeout=600)
    data=DataBlock(ts=np.arange(11),zs=[3]*10)
    await sa.put(data)
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)

@pytest.mark.asyncio
async def test_cluster_within_one_datablock_gives_NEW():
    sa = SmartAlert(threshold=0, timeout=600)
    d0 = DataBlock(ts=np.arange(11),zs=[0,0,0,1,1,1,1,1,0,0])
    await sa.put(d0)
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=range(3,9),zs=[1,1,1,1,1]))
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)

@pytest.mark.asyncio
async def test_cluster_within_two_datablock_gives_UPD():
    sa = SmartAlert(threshold=0, timeout=600)
    d0=DataBlock(ts=np.arange(0, 11),zs=[0,0,0,0,0,1,1,1,1,1])
    d1=DataBlock(ts=np.arange(10,21),zs=[2,2,2,2,2,0,0,0,0,0])
    await sa.put(d0)
    await sa.put(d1)
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=range(5,11),zs=[1,1,1,1,1]))
    assert await get(sa) == ("UPD",DataBlock(id=1,ts=range(5,16),zs=[1,1,1,1,1,2,2,2,2,2]))
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)


@pytest.mark.asyncio
async def test_cluster_rewritten_by_second_data_gives_DEL():
    sa = SmartAlert(threshold=0, timeout=600)
    d0 = DataBlock(ts=np.arange(11),zs=[0,0,0,1,1,1,1,1,0,0])
    d1 = DataBlock(ts=np.arange(11),zs=[0,0,0,0,0,0,0,0,0,0])
    await sa.put(d0)
    await sa.put(d1)
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=range(3,9),zs=[1,1,1,1,1]))
    assert await get(sa) == ("DEL",DataBlock(id=1,ts=range(3,9),zs=[1,1,1,1,1]))
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)

async def dump_all(obj):
    print('--beg')
    while True:
        try:
            res = await get(obj)
            print(res)
        except asyncio.TimeoutError:
            print('--end')
            return

@pytest.mark.asyncio
async def test_two_clusters_in_one_block():
    sa = SmartAlert(threshold=0, timeout=600)
    d0 = DataBlock(ts=np.arange(0, 11),zs=[0,1,1,1,0,0,2,2,2,0])
    await sa.put(d0)
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=[1,2,3,4], zs=[1,1,1]))
    assert await get(sa) == ("NEW",DataBlock(id=2,ts=[6,7,8,9], zs=[2,2,2]))
    
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)

@pytest.mark.asyncio
async def test_two_clusters_merge_by_z_order():
    sa = SmartAlert(threshold=0, timeout=600)
    d0 = DataBlock(ts=np.arange(0, 11),zs=[0,1,1,1,0,0,2,2,2,0])
    d1 = DataBlock(ts=np.arange(0, 11),zs=[0,0,0,2,2,2,2,0,1,1])
    await sa.put(d0)
    await sa.put(d1)
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=[1,2,3,4], zs=[1,1,1]))
    assert await get(sa) == ("NEW",DataBlock(id=2,ts=[6,7,8,9], zs=[2,2,2]))
    assert await get(sa) == ("UPD",DataBlock(id=2,ts=[3,4,5,6,7], zs=[2,2,2,2]))
    assert await get(sa) == ("DEL",DataBlock(id=1,ts=[1,2,3,4], zs=[1,1,1]))
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=[8,9,10], zs=[1,1]))
    
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)

@pytest.mark.asyncio
async def test_two_clusters_merge_to_two():
    sa = SmartAlert(threshold=0, timeout=600)
    d0 = DataBlock(ts=np.arange(0, 11),zs=[0,1,1,1,0,0,2,2,2,0])
    d1 = DataBlock(ts=np.arange(0, 11),zs=[0,0,0,1,1,1,1,0,2,2])
    await sa.put(d0)
    await sa.put(d1)
    assert await get(sa) == ("NEW",DataBlock(id=1,ts=[1,2,3,4], zs=[1,1,1]))
    assert await get(sa) == ("NEW",DataBlock(id=2,ts=[6,7,8,9], zs=[2,2,2]))
    assert await get(sa) == ("UPD",DataBlock(id=2,ts=[8,9,10], zs=[1,1]))
    assert await get(sa) == ("UPD",DataBlock(id=1,ts=[3,4,5,6,7], zs=[1,1,1,1]))
    
    with pytest.raises(asyncio.TimeoutError):
        await get(sa)

