import asyncio
from ..datablock import DataBlock
from .databuffer import DataBuffer
from .regions import RegionsQueue
import numpy as np
              
class Buffer:
    def __init__(self, delay=1, timeout=0, margin=[0,0]):
        self.db = DataBuffer()
        self.regions = RegionsQueue(margin=margin, delay=delay)

    async def put(self, data):
        t_drop = data.T1()-timeout
        self.db.put(data)
        await self.regions.put(data.T0(),data.T1())

    async def get(self):
        T0,T1 =  await self.regions.get()
        ts = self.db.slice_ts(T0,T1)
        zs = np.stack(self.db.at(ts)).T
        ids = list(self.db.clients.keys())
        return DataBlock(id=ids,ts=ts,zs=zs)

