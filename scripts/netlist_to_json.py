#!/usr/bin/env python

"""Convert a pickled netlist into JSON."""

import pickle

import json

from collections import defaultdict

from six import iteritems

from rig.machine import Cores, SDRAM, SRAM
from rig.netlist import Net


def netlist_to_json(netlist):
    """Convert a netlist into JSON."""
    next_id = [0]

    def new_id():
        next_id[0] += 1
        return str(next_id[0])

    vertices = defaultdict(new_id)

    vertices_resources = {
        vertices[v]: {str(r_): v_ for r_, v_ in iteritems(r)}
        for v, r in iteritems(netlist["vertices_resources"])}

    nets = [{"source": vertices[n.source],
             "sinks": [vertices[s] for s in n.sinks],
             "weight": float(n.weight)}
            for n in netlist["nets"]]

    return {"vertices_resources": vertices_resources,
            "nets": nets}


def json_to_netlist(json_netlist):
    """Convert a JSON-structured netlist into Rig/Python objects."""
    standard_resources = {
        "Cores": Cores,
        "SDRAM": SDRAM,
        "SRAM": SRAM,
    }

    vertices_resources = {
        v: {standard_resources.get(r, r): v
            for r, v in iteritems(rs)}
        for v, rs in iteritems(json_netlist["vertices_resources"])}

    nets = [Net(n["source"], n["sinks"], n["weight"])
            for n in json_netlist["nets"]]

    return {"vertices_resources": vertices_resources,
            "nets": nets}


if __name__=="__main__":
    import sys
    if len(sys.argv) != 2:
        print("Expected one argument: netlist.")
        sys.exit(1)
    else:
        with open(sys.argv[1], "rb") as f:
            netlist = pickle.load(f)
        print(json.dumps(netlist_to_json(netlist)))
