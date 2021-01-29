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
    """Fisher combination method """
    zs = np.ma.masked_invalid(data.zs)
    ps = np.ma.masked_array(z2p(zs),zs.mask)
    X = -2*np.sum(np.log(ps),axis=1)
    assert X.shape==(zs.shape[0],)
    Nexp = (zs.mask==False).sum(axis=1)
    pc = x2p(X, Nexp=Nexp)
    zc = p2z(pc)
    return DataBlock(ts=data.ts,zs=zc)

def Stouffer(weights: dict):
    """Stouffer combination method: 
    combined significance is linear combination of all significances:
        z_c = sum(z_i * w_i)

    Parameters
    -------
    weights: dict (srt, float)
        Mapping det_id: w_i, providing the coefficients for linear combination

    Weights don't need to be normalized: 
    the normalization is calculated depending on which detector ids are present in a given datablock id
    """
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
