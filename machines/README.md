Machines
========

This directory contains a set of JSON files describing SpiNNaker machines.


Machine JSON Format
-------------------

The format used for the JSON files.

    {"hostname": hostname,
     "width": width,
     "height": height,
     "chip_resources": {resource_name, value, ...},
     "chip_resource_exceptions": [[x, y, {resource_name, value, ...}], ...],
     "dead_chips": [[x, y], ...],
     "dead_links": [[x, y, link], ...],
    }

Where:

* `hostname` is the hostname of the SpiNNaker machine itself.
* `resource_name` is a string naming a resource. The following resource types
  are defined as being exactly equivilent to the corresponding Rig types:
  * "Cores"
  * "SDRAM"
  * "SRAM"
* The `value` of a resource is the integer amount of that resource consumed.
* `link` is an integer between 0 and 5, inclusive.

The `scripts/machine_to_json.py` script which takes the hostname of a SpiNNaker
machine and produces a machine JSON file on stdout.

    $ python machine_to_json.py HOSTNAME > machine.json

