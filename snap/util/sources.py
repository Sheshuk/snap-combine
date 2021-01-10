import numpy as np
import time
import asyncio

async def sleep_until(tnext):
        t0 = time.time()
        await asyncio.sleep(tnext-t0)
        
async def generate_data(dt, size):
    def gen_data(T0):
        delay = size*dt
        dts = np.linspace(0,delay,size+1)
        while True:
            T1 = T0+delay
            zs=np.random.normal(size=size).astype(float)
            yield T1,(T0+dts,zs)
            T0 = T1
    for T1,data in gen_data(T0 = float(time.time())):
        ts,zs = data
        yield {'ts':ts,'z':zs}
        await sleep_until(T1)
    
async def read_input(fname, size, columns, delay=0):
    import sys, asyncio
    from concurrent.futures import ThreadPoolExecutor

    fo = sys.stdin if fname=='stdin' else open(fname)
    with fo as f:
        loop = asyncio.get_event_loop()
        def do_read():
            res = np.loadtxt(f, usecols = columns.values(), unpack=True,max_rows=size)
            return dict(zip(columns, res))
        with ThreadPoolExecutor() as exe:
            while f:
                yield await loop.run_in_executor(exe, do_read)
                await asyncio.sleep(delay)

