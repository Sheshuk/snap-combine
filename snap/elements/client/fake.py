import asyncio
import sn_stat as st
import numpy as np
from datetime import datetime

def now():
    return datetime.now().timestamp()

async def sample_ts(B, S=0, tSN=0, tChunk=10):
    """ Data :term:`source`, generating random event timestamps 
    following the given rates, with signal injection.
    
    Args:
        B(rate)
            Background rate vs. time
        S(rate)
            Signal rate vs. time from signal start.
        tSN(float)
            Delay of the signal to start, after the generator started work.
    Yields:
        event timestamp in seconds
    """
    t0 = now()
    R = st.rate(B)+st.rate(S).shift(t0+tSN)
    while True:
        ts = st.Sampler(R,time_window=[t0,t0+tChunk]).sample()
        yield np.sort(ts)
        t0+=tChunk

async def realtime(source):
    """ 
    Output each timestamp from the list at their appropriate time

    :Input: list of unix timestamps
    :Output: yield each timestamp individually at their time.
    """
    async for data in source:
        for t in np.sort(data):
            await asyncio.sleep(t-now())
            yield t

class Generator:
    def __init__(self, B, S=0, tChunk=10):
        self.S = st.Signal(S, distance=1)
        self.tChunk=tChunk
        self.B=st.rate(B)
        self.R = self.B
        self.t0 = now()

    async def put(self, command):
        tSN = command['tSN']
        dist =command['dist']
        self.R = self.B+self.S.at(dist).shift(tSN)
        print(f"Expecting supernova @{dist}kpc at t={tSN} (in {tSN-now()} seconds!")

    async def get(self):
        ts = st.Sampler(self.R,
                time_window=[self.t0,self.t0+self.tChunk]).sample()
        self.t0+=self.tChunk
        return np.sort(ts)

async def detonator(delay=10):
    while True:
        tSN = now()+delay
        dist = 1.
        yield {'tSN':tSN, 'dist':dist}
