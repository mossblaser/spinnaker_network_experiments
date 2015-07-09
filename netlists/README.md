Netlists
========

This directory contains a set of reference netlists encoded as JSON.
These netlists contain only connectivity and do not contain
placement/allocations/routes.


JSON Format
-----------

    {"vertices_resources": {vertex_id: {resource_name: value, ...}},
     "nets": [{"source": vertex_id,
               "sinks": [vertex_id, ...],
               "weight": weight},
              ...],
    }

Where:

* `vertex_id` is a unique string identifying each vertex.
* `resource_name` is a string naming a resource. The following resource types
  are defined as being exactly equivilent to the corresponding Rig types:
  * "Cores"
  * "SDRAM"
  * "SRAM"
* The `value` of a resource is the integer amount of that resource consumed.
* `weight` is a positive float giving the weight of the net.

Conversion Script
-----------------

The `scripts/netlist_to_json.py` script accepts a conventional pickled netlist
and generates an equivilent JSON version on standard out.

    $ python netlist_to_json.py netlist.pcl > netlist.json
