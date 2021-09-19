import asyncio
import numpy as np
from snap.datablock import DataBlock

def find_clusters(data: DataBlock, thr: float):
    idx = np.nonzero(data.zs>thr)[0]
    #find the borders between groups
    borders = np.where(np.diff(idx, prepend=-np.inf, append=np.inf)>1)[0]
    #return each group
    res = []
    for i0,i1 in  zip(borders[:-1],borders[1:]):
        g  = idx[slice(i0,i1)]
        gt = np.append(g, g[-1]+1)
        res += [DataBlock(data.ts[gt],data.zs[g], id=data.id)]
    return res

class SmartAlert:
    """A precessing :term:`step` for detecting the parts (clusters) of the time series above threshold, 
    bookkeeping of these parts and producing 'NEW/UPD/DEL' commands  for these clusters.
    """
    clu_id = 0
    def __init__(self, threshold:float=5, timeout:float=600):
        """
        Args:
            thr (float)
                significance threshold
            timeout (float) 
                time in seconds for which the data is kept in buffer
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

        self.data = None
        self.thr = threshold
        self.timeout = timeout
        self.clusters = []
        self.queue = asyncio.Queue()
        
    def drop_tail(self):
        t_drop = self.data.T1()-self.timeout

        #drop obsolete clusters
        self.clusters = [c for c in self.clusters if(c.T1()>=t_drop)]
        #shift drop time to avoid cutting existing clusters
        for c in self.clusters:
            if t_drop in c:
                t_drop = c.T0()
        #cut the data
        self.data = self.data.drop_tail(t_drop)

    async def put(self, data: DataBlock):
        if self.data is None:
            self.data = data
        else:
            self.data = self.data.update(data)
        self.drop_tail()
        clusters = find_clusters(self.data, self.thr)
        res = self.update_clusters(clusters)
        for method,clus in res.items():
            for c in clus:
                print(method,c)
                await self.queue.put((method,c))

    async def get(self):
        return await self.queue.get()

    def update_clusters(self, clusters):
        """Update the current clusters with the new ones.
        This means:
            UPDATE old cluster, if it collides with a new cluster
            DELETE old cluster, if it doesn't collide to new clusters 
            CREATE new cluster if it didn't collide with any old ones

        Args:
            clusters (list)
                List of new clusters found
        Returns:
            dict:
                'DEL': list of clusters to delete
                'UPD': list of clusters to update
                'NEW': list of clusters to create
        """
        def collides(d0,d1):
            return not((d0.T1()<d1.T0())|(d1.T1()<d0.T0()))
        def maxz(d):
            return d.zs.max()

        to_upd = []
        to_old = []
        to_new = clusters
        to_del = self.clusters
        for c0 in sorted(self.clusters, key=maxz, reverse=True):
            for c1 in sorted(clusters, key=maxz, reverse=True):
                if collides(c0,c1):
                    c1.id = c0.id
                    to_del.remove(c0)
                    to_new.remove(c1)
                    if c1!=c0:
                        to_upd.append(c1)
                    else:
                        to_old.append(c1)
                    break
        #set IDs to new clusters
        for c in to_new:
            self.clu_id+=1
            c.id = self.clu_id
        self.clusters = to_old+to_new+to_upd
        return {'UPD': to_upd, 'DEL': to_del, 'NEW': to_new}

