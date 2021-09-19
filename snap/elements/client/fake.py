import asyncio
import sn_stat as st
import numpy as np
from snap import timing

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
    t0 = timing.now()
    R = st.rate(B)+st.rate(S).shift(t0+tSN)
    while True:
        ts = st.Sampler(R,time_window=[t0,t0+tChunk]).sample()
        yield np.sort(ts)
        t0+=tChunk

def realtime(shift:float=0):
    """ 
    Output each timestamp from the list at their appropriate time

    :Input: list of unix timestamps
    :Output: yield each timestamp individually at their time.

    Args:
        shift
            time shift in seconds
    """

    async def _f(source):
        async for data in source:
            for t in np.sort(data):
                await timing.wait_until(t+shift)
                yield t
    return _f

class Generator:
    def __init__(self, B, S=0, tChunk=10):
        self.S = st.Signal(S, distance=1)
        self.tChunk=tChunk
        self.B=st.rate(B)
        self.R = self.B
        self.t0 = timing.now()

    async def put(self, command):
        tSN = command['tSN']
        dist =command['dist']
        self.R = self.B+self.S.at(dist).shift(tSN)
        print(f"Expecting supernova @{dist}kpc at t={tSN} (in {tSN-timing.now()} seconds!")

    async def get(self):
        ts = st.Sampler(self.R,
                time_window=[self.t0,self.t0+self.tChunk]).sample()
        self.t0+=self.tChunk
        return np.sort(ts)

async def detonator(delay=10):
    while True:
        tSN = timing.now()+delay
        dist = 1.
        yield {'tSN':tSN, 'dist':dist}
