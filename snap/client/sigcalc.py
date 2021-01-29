from sn_stat import SigCalc, LLR
from snap.datablock import DataBlock
import numpy as np
from snap.util import timing

class ShapeAnalysis:
    """Significance calculator using shape analysis
    
       Calculates SN observation significance using shape analysis method, 
       based on the *sn_stat* module.

       Calculator consumes the data timestamps (via :ShapeAnalysis.put: method) 
       and produces :snap.datablock.DataBlock: with the SN observation significance 


       """
    def __init__(self,S,B, time_window, dt=0.1, tChunk_min=1, **params):
        """
        Create significance calculator with given bg and sg rates

        params:
        -------
            * S, B: signal and background rates (see note)
            * time_window: tuple (t0,t1) - a range around expected supernova time,
            where we perform analysis
            * dt: float, time step of the start location
            * tChunk_min: minimal time duration of the produced chunk of data
        """
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
        """ Add the data (events time series) """
        self.data=np.append(self.data,data)

    async def get(self) -> DataBlock:
        """Calculate the significance and return it in a :snap.DataBlock: """
        tw0,tw1 = self.time_window 
        time_start = self.t0+tw1-tw0
        await timing.wait_until(time_start, self.tChunk_min)
        t1 = timing.now()
        #define time regions
        ts = np.arange(self.t0-tw0,t1-tw1, self.dt)
        #calculate significance
        zs = self.sc([self.data], ts)
        #drop obsolete data
        t_last = ts[-1]+self.dt
        self.drop_tail(t_last + tw0)
        return DataBlock(np.append(ts,t_last),zs)
