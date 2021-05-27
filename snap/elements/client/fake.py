import asyncio
from sn_stat import Sampler, rate
from snap import timing
import numpy as np

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
    R = rate(B)+rate(S).shift(tSN)
    t0 = 0
    while True:
        ts = Sampler(R,time_window=[t0,t0+tChunk]).sample()
        ts=np.sort(ts)
        for t in ts:
            await asyncio.sleep(t-t0)
            t0=t
            yield timing.now()

