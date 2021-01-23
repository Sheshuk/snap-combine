from dataclasses import dataclass
import numpy as np

@dataclass
class DataBlock:
    ts: np.ndarray
    zs: np.ndarray

    def __repr__(self):
        s = '\n'.join([f'{t:10.3f} {z:5.3f}'for t,z in zip(self.ts, self.zs)])
        return '#ts zs\n'+ s
            

