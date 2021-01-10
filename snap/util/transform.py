import numpy as np

def time_transform(shift=1262304000, factor=1e-3):
    def _transform(data):
        data['ts'] = data['ts']*factor+shift
        return data
    return _transform

def time_precision(precision=5e-3):
    def _transform(data):
        data['ts'] = np.floor(data['ts']/precision)*precision
        return data
    return _transform

def append_bin_edge(data):
    ts = data['ts']
    data['ts'] = np.append(ts,2*ts[-1]-ts[-2])
    return data

def set(**kwargs):
    def _f(data):
        data.update(kwargs)
        return data
    return _f

