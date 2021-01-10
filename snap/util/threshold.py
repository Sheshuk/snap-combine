import asyncio
import numpy as np

class Threshold:
    def __init__(self, thr):
        self.thr=thr
        self.queue = asyncio.Queue()

    async def put(self,data):
        ts = data.pop('ts')
        zs = data.pop('z')
        for t,z in self.find_clusters(ts,zs):
            await self.queue.put({'ts':t,'z':z,**data})

    async def get(self):
        return await self.queue.get()

    def find_clusters(self, ts,zs):
        idx = np.nonzero(zs>self.thr)[0]

        #find the borders between groups
        borders = np.where(np.diff(idx, prepend=0, append=0)!=1)[0]
        #return each group
        for i0,i1 in  zip(borders[:-1],borders[1:]):
            g  = idx[slice(i0,i1)]
            gt = np.append(g, g[-1]+1)
            yield ts[gt],zs[g]
