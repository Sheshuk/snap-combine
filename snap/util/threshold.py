import asyncio
import numpy as np
from snap.datablock import DataBlock

class Threshold:
    def __init__(self, thr):
        self.thr=thr
        self.queue = asyncio.Queue()

    async def put(self, data: DataBlock):
        for d in self.find_clusters(data):
            await self.queue.put(d)

    async def get(self):
        return await self.queue.get()

    def find_clusters(self, data: DataBlock):
        idx = np.nonzero(data.zs>self.thr)[0]
        #find the borders between groups
        borders = np.where(np.diff(idx, prepend=0, append=0)!=1)[0]
        #return each group
        for i0,i1 in  zip(borders[:-1],borders[1:]):
            g  = idx[slice(i0,i1)]
            gt = np.append(g, g[-1]+1)
            yield DataBlock(data.ts[gt],data.zs[g])
