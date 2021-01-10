import snap

import numpy as np
import pandas as pd
import functools

def combine_function(data,method):
    df = data['df']
    interval = data['interval']
    if df.empty:
        return None
    #prepare table by experiments
    dfi = df.pivot_table(columns = ['eID'], index=('t0'), values=['z','t1'])
    #add the missing time points (where the bins end)
    t_stops = np.setdiff1d(df.t1,df.t0)
    df_stops = pd.DataFrame(index = t_stops, columns=dfi.columns)
    dfi = pd.concat([dfi, df_stops]).sort_index()
    #propagate the points forward in bins
    dfi = dfi.fillna(method='ffill')
    
    #drop points outside the interval
    dfi = dfi[slice(*interval)]
    
    #remove points, propagated too far
    to_remove = dfi.t1.values<=np.expand_dims(dfi.index,1)
    dfi.z.values [to_remove] = np.nan
    dfi.t1.values[to_remove] = np.nan
    if dfi.empty:
        return None
    #do combine
    zs = method(dfi)
    ts = dfi.index.values
    return {'ts':ts,'z':zs}


def Combiner(combine):
    return snap.Parallel(functools.partial(combine_function,method=combine), 
                    executor='process')
