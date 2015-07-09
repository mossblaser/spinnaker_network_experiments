Results
=======

This directory contains a hierarchy of subdirectories as follows:

     results/
     |-- totals.csv
     |-- router_counters.csv
     |-- totals/
     |   |-- placer_name/
     |   |   |-- machine_name/
     |   |   |   |-- netlist_name.csv
     |   |   |   |-- ...
     |   |   |-- ...
     |   |-- ...
     |-- router_counters/
     |   |-- ...

Results
-------

All results files will contain the following label columns:

* `netlist` the name of the network which was tested
* `placer` the name of the placement algorithm
* `placement_duration` the name of the placement algorithm
* `injection_rate` the number of packets-per-second-per-unit-weight for each
  net in the given sample.
* `duration` the number of seconds the group ran for
Experiment execution
--------------------

The `scripts/experiment.py` script which takes a netlist, placement, machine
and SpiNNaker board hostname and produces a pair of CSV results files.

    $ python experiment.py netlist.json placements.json machine.json \
                           totals.csv router_counters.csv