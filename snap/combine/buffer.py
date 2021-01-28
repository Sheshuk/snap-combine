import asyncio
from ..datablock import DataBlock
from .databuffer import DataBuffer
from .regions import RegionsQueue
import numpy as np
              
class Buffer:
    def __init__(self, delay=1, timeout=6000, margin=[0,0]):
        self.db = DataBuffer()
        self.regions = RegionsQueue(delay=delay)
        self.timeout = timeout

    async def put(self, data):
        t_drop = data.T1()-self.timeout
        self.db.put(data)
        await self.regions.put(data.T0(),data.T1())
        self.db.drop_tail(t_drop)

    async def get(self):
        T0,T1 =  await self.regions.get()
        ts = self.db.slice_ts(T0,T1)
        tc = 0.5*(ts[:-1]+ts[1:])
        zs = self.db.at(tc)
        ids = list(self.db.clients.keys())
        return DataBlock(id=ids,ts=ts,zs=zs)

