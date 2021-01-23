from sn_stat import SigCalc, LLR
from snap.datablock import DataBlock
import numpy as np
from snap.util import timing

class SigCalculator:
    """Significance calculator using shape analysis
    
       Calculates SN observation significance using shape analysis method, 
       based on the *sn_stat* module """
    def __init__(self,S,B, time_window, dt=0.1, tChunk_min=1, **params):
        llr = LLR(S,B,time_window)
        self.sc = SigCalc([llr],**params)
        self.time_window = time_window
        self.t0 = timing.now()
        self.dt=dt
        self.tChunk_min = tChunk_min
        self.data = np.array([])
    
    def drop_tail(self,t_drop):
        self.data = self.data[self.data>=t_drop]
        self.t0 = t_drop

    async def put(self, data):
        self.data=np.append(self.data,data)

    async def get(self):
        tw0,tw1 = self.time_window 
        time_start = self.t0+tw1-tw0
        await timing.wait_until(time_start, self.tChunk_min)
        t1 = timing.now()
        #define time regions
        ts = np.arange(self.t0-tw0,t1-tw1, self.dt)
        #calculate significance
        zs = self.sc([self.data], ts)
        #drop obsolete data
        self.drop_tail(ts[-1]+self.dt + tw0)
        return DataBlock(ts,zs)
