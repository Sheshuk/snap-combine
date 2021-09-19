from dataclasses import dataclass
import numpy as np

PRECISION=1e-8

@dataclass(init=False, eq=False)
class DataBlock:
    ts: np.ndarray
    zs: np.ndarray
    id: str = None

    def __init__(self, ts, zs, id=None):
        """Container for the significance time series. 

        Significance is defined in time bins, so minimal data block can contain a single `zs` value, but two `ts` value, defining the time limits of this significance estimation.

        Args:
            ts (iterable of float) 
                Time bin edges
            zs (iterable of float)
                Significance values for each time bin. Must be 1 value shorter than `ts`.
            id (str)
                Identifier of whatever created this datablock.
                
        """
        self.ts = np.array(ts, dtype=np.float64)
        self.zs = np.array(zs, dtype=np.float64)
        self.id=id
        if(len(zs)!=len(ts)-1):
            raise ValueError(f"DataBlock sizes mismatch: ts ({len(ts)}) != zs ({len(zs)})+1")

    def T0(self):
        "Lower time limit"
        return self.ts[0]
    def T1(self):
        "Upper time limit"
        return self.ts[-1]
    def __contains__(self, t):
        """Check if given t is contained in this datablock, 
        i.e. (t>=T0)and(t<T1)
        """
        return (t>=self.T0())&(t<self.T1())

    def __len__(self):
        return len(self.zs)

    def __str__(self):
        s = '\n'.join([f'{t:10.3f} {z:5.3f}'for t,z in zip(self.ts, self.zs)])
        return f'#{self.id}: ts zs\n'+ s
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        try:
            return (self.id==other.id) & \
                    len(self)==len(other) & \
                    np.allclose(self.ts,other.ts)& \
                    np.allclose(self.zs,other.zs,equal_nan=True)
        except:
            return False

    def __add__(self, other):
        """ Concatenate two datablocks of the same id"""
        if(self.id!=other.id):
            raise ValueError(f"Cannot add DataBlocks with d1.id={self.id} != d2.id={self.id}")
        if(np.isclose(self.T1(),other.T0(),atol=PRECISION)):
            return DataBlock(
                    id=self.id, 
                    ts = np.concatenate([self.ts, other.ts[1:]]),
                    zs = np.concatenate([self.zs, other.zs])
                    )
        elif(self.T1()<other.T0()):
            return DataBlock(
                    id=self.id, 
                    ts = np.concatenate([self.ts, other.ts]),
                    zs = np.concatenate([self.zs,[np.nan], other.zs])
                    )
        else:
            raise ValueError(f"Cannot add DataBlocks with d1.T1={self.T1()} > d2.T0={other.T0()}")


    def find_idx(self, ts, clip:bool = False):
        idx=np.searchsorted(self.ts, ts, side='right')-1
        if(clip):idx=np.clip(idx,0,len(self.zs))
        return idx

    def at(self, t):
        """Return z value at given time. If outside range, return NaN"""
        idx = self.find_idx(t,clip=False)
        idx = np.array(idx)
        idx[idx>len(self.zs)-1]=-1
        res = np.array(self.zs[idx])
        res[idx<0] = np.nan
        return res

    def apply_precision(self, precision=1e-3):
        """Round timestamps to given precision"""
        self.ts = precision*np.round(self.ts/precision)
        return self

    def drop_tail(self, t0):
        """Create new datablock with the data above given t0"""
        if t0<self.T0():
            ts = self.ts
            zs = self.zs
        else:
            idx = self.find_idx(t0, clip=False)
            ts = np.append([t0],self.ts[idx+1:])
            zs = self.zs[idx:]

        return DataBlock(id=self.id,ts=ts,zs=zs)

    def add_time_point(self, t):
        """Split the bin at time t
        i.e. for bin ([t0,t1],z) split_time(t) will produce two bins: ([t0,t],z),([t,t1],z)
        However if t==t0 or t==t1, the data will be unchanged.

        Args:
            t (float or floats)
                Timstamp where to split the data
        Returns:
            DataBlock with original data, but with one bin split.

        """
        
        #discard values already contained in ts:
        t = set(t).difference(self.ts) 
        t = [tv for tv in t if (tv in self)]
        
        idx = np.searchsorted(self.ts,t)
        
        ts = np.insert(self.ts,idx,t)
        zs = np.insert(self.zs,idx-1,self.at(t))
        return DataBlock(id=self.id,ts=ts,zs=zs)

    def update(self, d):
        """ Update this datablock with the data from another one.
        This will rewrite the data within [d.T0,d.T1], and leave the other data unchaned.

        Args:
            d (DataBlock)
                The new data, to update the current datablock
        Returns:
            DataBlock containing data from the original one, with updates from `d`
        """
        d0 = self.add_time_point([d.T0(), d.T1()])
        i0 = d0.ts< d.T0()
        i1 = d0.ts> d.T1()
        ts = np.concatenate([d0.ts[i0],d.ts,d0.ts[i1]])

        i0,i1 = i0[:-1],i1[1:]
        zs = d.zs
        #add nan bin to zs if there is distance 
        if(d.T0()>d0.T1()): 
            zs = np.insert(zs, 0,np.nan)
        elif(d.T1()<d0.T0()): 
            zs = np.insert(zs,len(zs),np.nan)

        zs = np.concatenate([d0.zs[i0],zs,d0.zs[i1]])
        return DataBlock(id=self.id,ts=ts,zs=zs)

