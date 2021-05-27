from snap.elements.combine.methods import Fisher, Stouffer
from snap.datablock import DataBlock
import numpy as np
from hypothesis import given, strategies as st
from hypothesis.extra import numpy as nps
import pytest

z_value = st.floats(-5, 5)
n_points = st.integers(1, 100)
n_clients= st.integers(1, 5)


def make_DataBlock(zs, ids:str='c_{n}'):
    return DataBlock(zs=zs,
            ts=np.linspace(0, 10, zs.shape[0]+1),
            id=[ids.format(n=n) for n in range(zs.shape[1])]
            )

def normal_DataBlock(shape, ids:str='c_{n}'):
    return make_DataBlock(zs = np.random.normal(size=shape),ids=ids)

def datablocks(npoints: int, nclients: int):
    return st.builds(make_DataBlock, 
            zs=nps.arrays(dtype=float, shape=(npoints,nclients), elements=z_value),
            )


@given(d=datablocks(1000, nclients=1))
def test_Fisher_single_changes_nothing(d):
    d1 = Fisher(d)
    #assert d1.zs.shape ==(len(d.zs),)
    assert np.allclose(d1.zs,d.zs[:,0], rtol=1e-5)

@given(d=datablocks(1000,nclients=3))
def test_Fisher_single_with_nans_changes_nothing(d):
    d.zs[:,0]=np.nan
    d.zs[:,2]=np.nan
    d1 = Fisher(d)
    assert np.allclose(d1.zs,d.zs[:,1])

@given(n_clients)
def test_Fisher_normal_distr(nc):
    n=100000
    d = normal_DataBlock((n,nc))
    assert np.isclose(d.zs.mean(),0, atol=1e-2)
    assert np.isclose(d.zs.std(), 1, atol=1e-2)
    d1 = Fisher(d)
    assert d1.zs.shape == (n,)
    assert np.isclose(d1.zs.mean(),0, atol=1e-2)
    assert np.isclose(d1.zs.std(), 1, atol=1e-2)

#-----------------------------------------
w_val=st.floats(1e-3,1e3)

@st.composite
def ws_dicts(draw, Nc,ids='c_{n}'):
    ids=[ids.format(n=n) for n in range(Nc)]
    vals = draw(st.lists(w_val,min_size=Nc, max_size=Nc))
    return dict(zip(ids,vals))


@given(d=datablocks(10,nclients=1), ws=ws_dicts(Nc=1))
def test_Stouffer_single_changes_nothing(d, ws):
    assert all(c in ws for c in d.id)
    d1 = Stouffer(ws)(d)
    assert np.allclose(d1.zs,d.zs[:,0], rtol=1e-5)

@given(d=datablocks(1000,nclients=3), ws=ws_dicts(Nc=3))
def test_Stouffer_single_with_nans_changes_nothing(d,ws):
    d.zs[:,0]=np.nan
    d.zs[:,2]=np.nan
    d1 = Stouffer(ws)(d)
    assert np.allclose(d1.zs,d.zs[:,1])

@given(st.data())
def test_Stouffer_normal_distr(data):
    Nc=data.draw(n_clients)
    Np=100000
    d = normal_DataBlock((Np,Nc))
    assert np.isclose(d.zs.mean(),0, atol=1e-2)
    assert np.isclose(d.zs.std(), 1, atol=1e-2)
    ws = data.draw(ws_dicts(Nc))
    d1 = Stouffer(ws)(d)
    assert d1.zs.shape == (Np,)
    assert np.isclose(d1.zs.mean(),0, atol=1e-2)
    assert np.isclose(d1.zs.std(), 1, atol=1e-2)


