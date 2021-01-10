import numpy as np
from record import Record
import combiner
from sorted_intervals import SortedIntervals

def gen_points(ts):
    t0s = ts[:-1]
    t1s = ts[1: ]
    points = [Record(expID=0, t0=t0,t1=t1,z=0) for t0,t1 in zip(t0s,t1s)]
    return points

def test_intervals():
    ts = np.arange(10)
    points = gen_points(ts)
    tsI = combiner._get_intervals(points)
    print(tsI)
    assert (np.all(tsI==ts))


def test_get_points():
    ts = np.arange(10)
    points = gen_points(ts)
    data = SortedIntervals(points)
    ts = combiner._get_intervals(points)
    t0s = ts[:-1]
    t1s = ts[1:]
    res = []
    for t0,t1 in zip(t0s,t1s):
        ps = data.get_points(t0lims=(None,t1),t1lims=(t0,None))
        print(t0,t1,ps)
        assert(len(ps)==1)

def  test_two_clients():
    ts1 = np.arange(10)
    points1 = gen_points(ts1)
    ts2 = 0.25+np.arange(10)
    points2 = gen_points(ts2)

    
