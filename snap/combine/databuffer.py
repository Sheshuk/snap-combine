from ..datablock import DataBlock

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
        return [c.at(ts) for c in self.clients]

    def slice_ts(self,t0,t1):
        """Get all the unique bin edges in given interval"""
        ts=[c.ts[(c.ts>t0)&(c.ts<t1)] for c in self.clients]
        ts = np.concatenate(ts+[[t0,t1]])
        return np.unique(ts)

