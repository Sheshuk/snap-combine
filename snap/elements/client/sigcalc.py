import sn_stat as sn
from snap.datablock import DataBlock
import numpy as np
from snap.util import timing

class SignificanceCalculator:
    """Significance calculator using shape analysis
    
       Calculates SN observation significance using the analysis method, 
       based on the *sn_stat* module.

       Calculator consumes the data timestamps (via :ShapeAnalysis.put: method) 
       and produces :snap.datablock.DataBlock: with the SN observation significance 


       """
    def __init__(self, ana, dt=0.1, tChunk_min=1):
        """
        Create significance calculator with given bg and sg rates

        Args:
            ana (:class:`sn.ShapeAnalysis` or :class:`sn.CountingAnalysis` object):
                analysis to be used for the significance calculation
            dt (float): 
                time step, seconds
            tChunk_min (float): 
                minimal time duration of the produced chunk of data
        """
        self.ana = ana
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
        tw0,tw1 = self.ana.det.time_window 
        time_start = self.t0+tw1-tw0
        await timing.wait_until(time_start, self.tChunk_min)
        t1 = timing.now()
        #define time regions
        ts = np.arange(self.t0-tw0,t1-tw1, self.dt)
        #calculate significance
        zs = self.ana(self.data, ts)
        #drop obsolete data
        t_last = ts[-1]+self.dt
        self.drop_tail(t_last + tw0)
        return DataBlock(np.append(ts,t_last),zs)

def CountAna(B, time_window, *, dt=0.1, tChunk_min=1):
    ana = sn.CountingAnalysis(
            sn.DetConfig(B=B, time_window=time_window)
            )
    return SignificanceCalculator(ana, dt, tChunk_min)

def ShapeAna(B,S, time_window="auto", *, dt=0.1, tChunk_min=1):
    ana = sn.ShapeAnalysis(
            sn.DetConfig(B=B,S=S,time_window=time_window)
            )
    return SignificanceCalculator(ana, dt, tChunk_min)