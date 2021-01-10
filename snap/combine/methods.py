import numpy as np

def Fisher(dfi):
    from scipy.stats import norm,chi2
    def z2p(z):
        return norm.sf(z)
    def p2z(p):
        return norm.isf(p)
    def x2p(x, Nexp):
        return chi2.sf(x, df=2*Nexp)
    
    zs = np.nan_to_num(dfi.z.values.T[:,:-1])
    ps = z2p(zs)
    X = -2*np.sum(np.log(ps),axis=0)
    p1 = x2p(X, Nexp=zs.shape[0])
    z1 = p2z(p1)
    return z1

class Stouffer:
    def __init__(self, weights):
        self.weights=weights
    def __call__(self,dfi):
        zs = np.nan_to_num(dfi.z.values.T[:,:-1])
        ws = np.array([self.weights.get(e,0) for e in dfi.z.columns])
        w2 = np.sqrt(np.sum(ws**2))
        zs = (ws*zs.T).sum(axis=1)
        return zs/w2 if w2>0 else 0


