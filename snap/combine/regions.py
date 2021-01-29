import asyncio
import numpy as np

class RegionsQueue:
    def __init__(self, delay=0):
        self.regions = []
        self.delay=delay
        self.has_new_data = asyncio.Event()

    def _add_and_merge(self,t0,t1):
        if(t1<t0):
            raise ValueError(f"Values {t0},{t1} not in ascending order")
        if len(self.regions)==0:
            self.regions=[(t0,t1)]
            return
        reg = np.array(self.regions+[(t0,t1)])
        collides = (reg[:,0]<=t1)&(reg[:,1]>=t0)
        to_merge = reg[collides]
        merged = (to_merge[:,0].min(), to_merge[:,1].max())
        self.regions = list(reg[collides==False]) + [merged]

    async def put(self, t0,t1):
        self._add_and_merge(t0,t1)
        self.has_new_data.set()
       
    async def _schedule(self,t0,t1, delay):
        await asyncio.sleep(delay)
        self._add_and_merge(t0,t1)

    async def get(self):
        if not self.regions:
            self.has_new_data.clear()
            await asyncio.sleep(self.delay)
        await self.has_new_data.wait()
        return self.regions.pop(0)

 

