from dataclasses import dataclass
import numpy as np

@dataclass(init=False, eq=False)
class DataBlock:
    ts: np.ndarray
    zs: np.ndarray
    id: str = None

    def __init__(self, ts, zs, id=None):
        self.ts = np.array(ts)
        self.zs = np.array(zs)
        self.id=id
        if(len(zs)!=len(ts)-1):
            raise ValueError(f"DataBlock sizes mismatch: ts ({len(ts)}) != zs ({len(zs)})+1")

    def T0(self):
        return self.ts[0]
    def T1(self):
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
        if(self.T1()>other.T0()):
            raise ValueError(f"Cannot add DataBlocks with d1.T1={self.T1()} > d2.T0={other.T0()}")

        if(self.T1()==other.T0()):
            return DataBlock(
                    id=self.id, 
					ts = np.concatenate([self.ts, other.ts[1:]]),
                    zs = np.concatenate([self.zs, other.zs])
                    )
        else:
            return DataBlock(
                    id=self.id, 
					ts = np.concatenate([self.ts, other.ts]),
                    zs = np.concatenate([self.zs,[np.nan], other.zs])
                    )


    def find_idx(self, ts, clip:bool = False):
        idx=np.searchsorted(self.ts, ts, side='right')-1
        if(clip):idx=np.clip(idx,0,len(self.zs))
        return idx

    def at(self, t):
        idx = self.find_idx(t,clip=False)
        idx[idx>len(self.zs)]=-1
        res = self.zs[idx]
        idx[idx<0] = np.nan

        
    def slice(self, t0,t1):
        i0,i1 = self.find_idx([t0,t1], clip=True)
        i1+=1
        ts=self.ts[i0:i1+1]
        #clip the limits to requested
        ts[0 ] = max(ts[0], t0)
        ts[-1] = min(ts[-1],t1)
        return DataBlock(id=self.id, ts=ts, zs=self.zs[i0:i1])


