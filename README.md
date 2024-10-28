# snap-combine 
![Tests](https://github.com/Sheshuk/snap-combine/workflows/Python%20package/badge.svg) ![Deploy](https://github.com/Sheshuk/snap-combine/workflows/Upload%20Python%20Package/badge.svg) ![PyPI](https://img.shields.io/pypi/v/snap-combine) ![release](https://img.shields.io/github/v/release/Sheshuk/snap-combine?include_prereleases) 

Code for combining SN significance from several detectors/experiments.

This package contains plugins for [SNAP](https://github.com/Sheshuk/snap-base) framework.

[Documentation](https://snap-combine.readthedocs.io)

## Installation
```
python -m pip install snap-combine
```

## Example

Example configurations provided the `examples` dir use these steps to 
* [client_sender.yml](examples/client_sender.yml): generate client data, calculate significance and send it (via ipc zeromq socket) to combiner node
* [combine.yml](examples/combine.yml): receive client significance time series, combine them and apply thresholds.

On client side run 
```
DETECTOR="det_name_1" snap_run client_sender.yml
```

Optionally in another terminal session:
```
DETECTOR="det_name_2" snap_run client_sender.yml
```

In another session (combination side):
```
snap_run combine.yml
```

You should see the monitoring ticks for all nodes.
Also you should see the files with the data output: `data_received.dat`,`data_combined.dat` and `data_triggered.dat`.

After about 120s from the client start, a supernova signal will be emitted, so the significance becomes elevated, and the Trigger counter will advance.
