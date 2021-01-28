from ..datablock import DataBlock
import numpy as np

class DataBuffer:
    def __init__(self, time_precision=1e-5):
        self.time_precision=time_precision
        self.clients = {}

    def put(self, data: DataBlock):
        """Add DataBlock to the buffer"""
        if data.id in self.clients:
            self.clients[data.id]+=data
        else:
            self.clients[data.id]=data

    def at(self, ts):
        """Return client values at given times"""
        return [d.at(ts) for d in self.clients.values()]

    def slice_ts(self,t0,t1):
        """Get all the unique bin edges in given interval"""
        ts=[d.ts[(d.ts>t0)&(d.ts<t1)] for d in self.clients.values()]
        ts = np.concatenate(ts+[[t0,t1]])
        return np.unique(ts)

    def drop_tail(self, t0):
        """Drop data older that t0"""
        for d in self.clients.values():
            d = d.drop_tail(t0)

