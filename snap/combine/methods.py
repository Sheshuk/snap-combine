import numpy as np
from scipy.stats import norm,chi2
from ..datablock import DataBlock
def z2p(z):
    return norm.sf(z)
def p2z(p):
    return norm.isf(p)
def x2p(x, Nexp):
    return chi2.sf(x, df=2*Nexp)

def Fisher(data: DataBlock) -> DataBlock:
    zs = np.ma.masked_invalid(data.zs)
    ps = np.ma.masked_array(z2p(zs),zs.mask)
    X = -2*np.sum(np.log(ps),axis=1)
    assert X.shape==(zs.shape[0],)
    Nexp = (zs.mask==False).sum(axis=1)
    pc = x2p(X, Nexp=Nexp)
    zc = p2z(pc)
    return DataBlock(ts=data.ts,zs=zc)

def Stouffer(weights: dict):
    def _f(data: DataBlock) -> DataBlock:
        zs = np.ma.masked_invalid(data.zs)
        #calculate weights for each point
        ws = np.array([weights[c] for c in data.id])
        ws = ws*(zs.mask==False)
        #calculate weights norm
        w2 = np.sqrt(np.sum(ws**2, axis=1))
        zc = (ws*zs).sum(axis=1)
        zc = (zc/w2).T
        return DataBlock(ts=data.ts,zs=zc)
    return _f
