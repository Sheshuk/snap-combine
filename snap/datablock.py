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
    def __len__(self):
        return len(self.zs)

    def __str__(self):
        s = '\n'.join([f'{t:10.3f} {z:5.3f}'for t,z in zip(self.ts, self.zs)])
        return f'#{self.id}: ts zs\n'+ s

    def __eq__(self, other):
        return (self.id==other.id) & np.allclose(self.ts,other.ts)& \
            np.allclose(self.zs,other.zs,equal_nan=True)

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

