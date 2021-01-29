import sys, asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np

async def read_file(fname, size, columns, delay=0):
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

