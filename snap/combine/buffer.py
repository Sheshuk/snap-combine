import logging
import asyncio
import pandas

import logging
import numpy as np

logger = logging.getLogger(__name__)

#decorators for additional functionality
def handle_collisions(cls):
    class _c(cls):
        async def put(self,data):
            ts = data['ts']
            collide = self.select(T0=ts[0],T1=ts[-1], eID=data['eID'])
            self.drop_points(collide)
            res = await super().put(data)
            return res
    return _c

def drop_tail(cls, timeout, save=None):

    class _c(cls):
        def __init__(self):
            super().__init__()

        def _drop_tail(self):
            T0 = self.Tlast-timeout
            return self.drop_points(self.df.t1<T0)
        async def put(self,data):
            res = await super().put(data)
            self.drop_tail()
            return res
        def _save_tail(self):
            tail = self._drop_tail()
            tail.to_hdf(save,'data',mode='a', append=True, format='table')

    _c.drop_tail = _c._drop_tail if save is None else _c._save_tail
    return _c

def only_eID(cls, eIDs):
    class _c(cls):
        async def put(self, data):
            if(data['eID'] in eIDs):
                await super().put(data)
    return _c
#--------------------
class DataBasePandas:
    def __init__(self):
        self.df = pandas.DataFrame(columns=['eID','t0','t1'])
        self.Tlast = 0
   
    async def put(self, data):
        self.Tlast = max(self.Tlast,data['ts'][-1])
        self.df = self.df.append(self._unpack(**data),ignore_index=True)
  
    def _unpack(self, eID,ts,**kwargs):
        try:
            size = len(ts)-1
            data = dict(eID=np.array([eID]*size),
                    t0=ts[:-1],
                    t1=ts[1: ],
                    **kwargs)
            return pandas.DataFrame(data)
        except ValueError:
            sizes = {a:len(kwargs[a]) for a in kwargs}
            sizes['ts'] = len(ts)
            raise ValueError(f"array lengths: {sizes}")
  
    def drop_points(self, selection):
        drop = self.df[selection]
        self.df = self.df[selection==False]
        return drop
    
    def select(self, T0,T1,**kwargs):
        sel = (self.df.t1>T0)&(self.df.t0<T1)
        for name,val in kwargs.items():
            sel &= self.df[name]==val
        return sel

    async def get(self, T0, T1, **kwargs):
        return self.df[self.select(T0, T1, **kwargs)]

class RegionsQueue:
    def __init__(self, margin=[0,0], delay=0):
        self.regions = []
        self.margin = margin
        self.delay=delay
        self.has_new_data = asyncio.Event()

    def _add_and_merge(self,t0,t1):
        reg = np.array(self.regions+[(t0,t1)])
        collides = (reg[:,0]<=t1)&(reg[:,1]>=t0)
        to_merge = reg[collides]
        merged = (to_merge[:,0].min(), to_merge[:,1].max())
        self.regions = list(reg[collides==False]) + [merged]

    async def put(self, data):
        ts = data['ts']
        t0,t1 = ts[0],ts[-1]
        task = self._schedule(t0+self.margin[0],t1+self.margin[1], delay=self.margin[1])
        asyncio.create_task(task)

    async def _schedule(self,t0,t1, delay):
        await asyncio.sleep(delay)
        self._add_and_merge(t0,t1)
        self.has_new_data.set()

    async def get(self):
        if not self.regions:
            self.has_new_data.clear()
            await asyncio.sleep(self.delay)
        await self.has_new_data.wait()
        return self.regions.pop()
               
class Buffer:
    def __init__(self, database, regions, wait_for_data=False):
        self.db = database
        self.regions = regions

    async def put(self, data):
        await self.db.put(data)
        await self.regions.put(data)

    async def get(self):
        T0,T1 =  await self.regions.get()
        points =  await self.db.get(T0,T1)
        return {'interval':(T0,T1),'df':points}

def CombinationBuffer(delay, timeout=1000):
    return Buffer(
            database =  handle_collisions(
                        drop_tail(timeout = timeout, save = None, cls=DataBasePandas)
                        )(),
            regions = RegionsQueue(delay=delay)
            )

def MonitoringBuffer(trigger_window=[-5,40], delay=40, timeout=100, filename='data_monitoring.hd5', trigger_id='Trigger'):
    return Buffer(
            database = drop_tail(DataBasePandas, timeout=timeout, save=filename)(),
            regions = only_eID(RegionsQueue, eIDs=['Trigger'])(margin=trigger_window,delay=delay)
            )

