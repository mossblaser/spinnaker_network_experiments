#!/usr/bin/env python

"""Place a netlist onto a machine, both supplied as a JSON description."""

import sys

import json

from importlib import import_module

import time

from six import iteritems

from rig.machine import Cores

from rig.place_and_route.constraints import ReserveResourceConstraint

from netlist_to_json import json_to_netlist
from machine_to_json import json_to_machine


def place_to_json(vertices_resources, nets, machine, algorithm="default"):
    """Place the specified netlist."""
    if algorithm == "default":
        module = "rig.place_and_route"
    else:
        module = "rig.place_and_route.place.{}".format(algorithm)
    
    try:
        placer = getattr(import_module(module), "place")
    except (ImportError, AttributeError):
        sys.stderr.write(
            "Placement algorithm {} does not exist\n".format(algorithm))
        sys.exit(1)
    
    constraints = [
        ReserveResourceConstraint(Cores, slice(0, 1))
    ]
    
    before = time.time()
    placements = placer(vertices_resources, nets, machine, constraints)
    after = time.time()
    
    return {"algorithm": algorithm,
            "placements": {v: [x, y] for v, (x, y) in iteritems(placements)},
            "placement_duration": after - before}


def json_to_placements(json_dict):
    """Get the placement duration and placement dictionary from an unpacked
    JSON representation."""
    return {"algorithm": json_dict["algorithm"],
            "placement_duration": json_dict["placement_duration"],
            "placements": {
                v: (x, y)
                for v, (x, y) in iteritems(json_dict["placements"])}
           }


if __name__=="__main__":
    import sys
    if len(sys.argv) != 4:
        print("Expected three arguments: netlist machine algorithm.")
        sys.exit(1)
    else:
        with open(sys.argv[1], "r") as f:
            netlist = json_to_netlist(json.load(f))
        with open(sys.argv[2], "r") as f:
            hostname, machine = json_to_machine(json.load(f))
        algorithm = sys.argv[3]
        print(json.dumps(place_to_json(netlist["vertices_resources"],
                                       netlist["nets"],
                                       machine,
                                       algorithm)))


