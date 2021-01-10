import asyncio

def blocking(delay):
    import time
    def _do(data):
        time.sleep(delay)
        return data
    return _do

def dump(data):
    print(f'DUMP: {data}')
    return data

def run_shell(cmd):
    async def _run(data):
        print(f"Run!")
        run_cmd = cmd.format(**data)
        print(f"Command to run: {run_cmd}")
        proc = await asyncio.create_subprocess_shell(run_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
                )
        stdout, stderr = await proc.communicate()
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')
        await proc.wait()
        return stdout.decode()
    
    return _run


def save_for_plot(filename):
    def save(data):
        eID,ts,zs = data['eID'],data['ts'],data['zs']
        fname = filename.format(eID=eID)
        with open(fname,'a') as f:
            t0s,t2s = ts[:-1],ts[1:]
            for t0,t1,z in zip(t0s,t1s,zs):
                f.write(f"{t0} {t1} {z}\n")
        return data
    return save

def trigger_notify(filename):
    async def _f(source):
        Ntrig = 0
        async for data in source:
            t0,t1 = data.get('interval')
            df    = data.get('df')
            Ntrig+=1
            print(f"========= TRIGGER {Ntrig}: {t0}-{t1} =========")
            print(f"saving data {len(df)} data points within {df.t0.min()} - {df.t1.max()}")

            with open(filename.format(n=Ntrig,t0=t0,t1=t1),'a') as f:
                df.to_csv(f, sep=' ')
            yield data
    return _f
