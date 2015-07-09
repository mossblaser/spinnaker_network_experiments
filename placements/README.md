Placements
==========

This directory contains a hierarchy of subdirectories as follows:

     placements/
     |-- placer_name/
     |   |-- machine_name/
     |   |   |-- netlist_name.json
     |   |   |-- ...
     |   |-- ...
     |-- ...

That is, we have a set of placements for every netlist using, every placement
algorithm, for various SpiNNaker machines.


Placements JSON format
----------------------

The format used for the `netlist_name.json` files.

    {"algorithm": algorithm_name,
     "placements": {vertex_id: [x, y], ...},
     "placement_duration": runtime,
    }

Where:

* `vertex_id` is a unique string identifying each vertex.
* `runtime` is the runtime of the placement algorithm in seconds


The `scripts/place.py` script which takes a netlist, machine and algorithm name
and produces a JSON file on stdout.

    $ python place.py netlist.json machine.json ALGORITHM > placements.json
