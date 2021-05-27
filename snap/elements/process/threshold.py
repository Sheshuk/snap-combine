import asyncio
import numpy as np
from snap.datablock import DataBlock

class Threshold:
    """ A processing :term:`step` for detecting and producing parts of time series above the given threshold. 
    """
    def __init__(self, thr):
        """
        Args:
            thr (float)
                significance threshold
        :Input:
            data (:class:`DataBlock`) with the time series (`zs` vs `ts`)
        :Output:
            :class:`DataBlock` containing cluster of values with `zs` above threshold.
            Will not output until such cluster is found.

        :Example:

        If the incoming data was::

            ts=[0,1,2,3,4,5,6,7,8,9,10]
            zs=[0,1,2,2,1,0,1,2,3,2,1 ]

        Then the found clusters for `thr=1` should be::

            1) ts=[2,3],  zs=[2,2]
            2) ts=[7,8,9],zs=[2,3,4]

        And they will be output in separate iterations.

        """
        self.thr=thr
        self.queue = asyncio.Queue()

    async def put(self, data: DataBlock):
        for d in self.find_clusters(data):
            await self.queue.put(d)

    async def get(self):
        return await self.queue.get()

    def find_clusters(self, data: DataBlock):
        idx = np.nonzero(data.zs>self.thr)[0]
        #find the borders between groups
        borders = np.where(np.diff(idx, prepend=0, append=0)!=1)[0]
        #return each group
        for i0,i1 in  zip(borders[:-1],borders[1:]):
            g  = idx[slice(i0,i1)]
            gt = np.append(g, g[-1]+1)
            yield DataBlock(data.ts[gt],data.zs[g])
