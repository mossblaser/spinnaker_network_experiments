Results
=======

This directory contains a hierarchy of subdirectories as follows:

     results/
     |-- totals.csv
     |-- router_counters.csv
     |-- chip_stats.csv
     |-- net_stats.csv
     |-- totals/
     |   |-- placer_name/
     |   |   |-- machine_name/
     |   |   |   |-- netlist_name.csv
     |   |   |   |-- ...
     |   |   |-- ...
     |   |-- ...
     |-- router_counters/
     |   |-- ...
     |-- chip_stats/
     |   |-- ...
     |-- net_stats/
     |   |-- ...

Results
-------

All results files will contain the following label columns:

* `netlist` the name of the network which was tested
* `machine` the name of the machine used
* `placer` the name of the placement algorithm
* `placement_duration` the name of the placement algorithm

Additionally, the `totals` and `router_counters` files have the following
columns:

* `injection_rate` the number of packets-per-second for the net with the
  greatest net.
* `reinject_packets` True or False depending on packet reinjection being used
  or not.
* `duration` the number of seconds the group ran for

Experiment execution
--------------------

The `scripts/experiment.py` script which takes a netlist, placement, machine
and SpiNNaker board hostname and produces a pair of CSV results files.

    $ python experiment.py netlist.json placements.json machine.json \
                           totals.csv router_counters.csv
