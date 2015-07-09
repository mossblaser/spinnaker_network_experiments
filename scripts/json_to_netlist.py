#!/usr/bin/env python

"""Given a fully placed netlist specified in JSON, produce a classic Rig-style
pickled netlist (e.g. for rig-par-diagram)."""

import sys

import pickle

import json

from six import iteritems

from rig.machine import Cores

from rig.place_and_route.constraints import ReserveResourceConstraint

from netlist_to_json import json_to_netlist
from machine_to_json import json_to_machine
from place import json_to_placements


if __name__=="__main__":
    import sys
    if len(sys.argv) != 5:
        print("Expected three arguments: netlist machine placements out.")
        sys.exit(1)
    else:
        with open(sys.argv[1], "r") as f:
            netlist = json_to_netlist(json.load(f))
        with open(sys.argv[2], "r") as f:
            hostname, machine = json_to_machine(json.load(f))
        with open(sys.argv[3], "r") as f:
            placements = json_to_placements(json.load(f))
        
        with open(sys.argv[4], "wb") as f:
            pickle.dump({
                "vertices_resources": netlist["vertices_resources"],
                "nets": netlist["nets"],
                "machine": machine,
                "constraints": [ReserveResourceConstraint(Cores, slice(0, 2))],
                "placements": placements["placements"],
            }, f)


