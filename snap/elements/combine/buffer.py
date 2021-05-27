import asyncio
from snap.datablock import DataBlock
from .databuffer import DataBuffer
from .regions import RegionsQueue
import numpy as np
              
class Buffer:
    """ Buffer which stores the incoming DataBlocks on :put:
    and provides the time slice of all the data in a recently updated region on :get:
    """
    def __init__(self, delay:float=1, timeout:float=6000):
        """Create the Buffer for the data

        params
        -----
            * delay, seconds - time to wait before processing a new region (on :get:)
            * timeout, seconds - defines how long will the data stay in the buffer (on :put:)
        """
        self.db = DataBuffer()
        self.regions = RegionsQueue(delay=delay)
        self.timeout = timeout

    async def put(self, data:DataBlock):
        t_drop = data.T1()-self.timeout
        self.db.put(data)
        await self.regions.put(data.T0(),data.T1())
        self.db.drop_tail(t_drop)

    async def get(self) -> DataBlock:
        T0,T1 =  await self.regions.get()
        ts = self.db.slice_ts(T0,T1)
        tc = 0.5*(ts[:-1]+ts[1:])
        zs = self.db.at(tc)
        ids = list(self.db.clients.keys())
        return DataBlock(id=ids,ts=ts,zs=zs)

