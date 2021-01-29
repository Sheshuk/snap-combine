# snap-combine 
![Tests](https://github.com/Sheshuk/snap-combine/workflows/Python%20package/badge.svg) ![Deploy](https://github.com/Sheshuk/snap-combine/workflows/Upload%20Python%20Package/badge.svg) ![PyPI](https://img.shields.io/pypi/v/snap-combine) ![release](https://img.shields.io/github/v/release/Sheshuk/snap-combine?include_prereleases) 

Code for combining SN significance from several detectors/experiments

This package contains plugins for [SNAP](https://github.com/Sheshuk/snap-base) framework.

## Installation
```
python -m pip install snap-combine
```

## Plugins

This package contains plugins which can be used in new snap pipeline configurations.

#### Monitoring: `snap.util.monitor`

* `tqdm_ticker`: a provides [tqdm](https://github.com/tqdm/tqdm)-based ticker, which counts the data flow and data rate through current step.

#### Generating client data: `snap.client.fake`

* `sample_ts`: Generates the neutrino interaction timestamps, using the given rate. Can simulate the supernova signal at the given time.

#### Processing client data: `snap.client`

* `sigcalc.ShapeAnalysis`: calculate supernova significance using shape analysis
* `setId`: change the datablock ID

#### Combination: `snap.combine`:

* `Buffer`: accumulate the data to synchrnize before combining
* `methods.Fisher`:   combine data using Fisher's combination method
* `methods.Stouffer`: combine data using Stouffer's combination method

#### Triggering: `snap.util.threshold`

* Threshold: select and forward only portions of data with significance above given threshold

#### Misc: `snap.util`

* `dump_to_file`: Dump data to given file

## Example

Example configurations provided the `examples` dir use these steps to 
* [client_sender.yml](examples/client_sender.yml): generate client data, calculate significance and send it (via ipc zeromq socket) to combiner node
* [combine.yml](examples/combine.yml): receive client significance time series, combine them and apply thresholds.

On client side run 
```
snap client_sender.yml -n node1
```

Optionally in another session:
```
snap client_sender.yml -n node2
```

In another session (combination side):
```
snap combine.yml
```

You should see the monitoring ticks for all nodes.
Also you should see the files with the data output: `data_received.dat`,`data_combined.dat` and `data_triggered.dat`.

After about 120s from the client start, a supernova signal will be emitted, so the significance becomes elevated, and the Trigger counter will advance.
