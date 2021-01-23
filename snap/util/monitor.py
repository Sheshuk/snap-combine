from tqdm.asyncio import tqdm
def tqdm_ticker(**kwargs):
    async def _f(source):
        with tqdm(source, **kwargs) as t:
            async for d in t:
                yield d
    return _f

def tqdm_meter(**kwargs):
    t = tqdm(**kwargs)
    def _f(d):
        val = d.zs.max()
        t.n = val
        t.update(0)
        return d
    return _f
