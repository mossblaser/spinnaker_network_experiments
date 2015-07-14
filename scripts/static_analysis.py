#!/usr/bin/env python

"""Calculate routing metrics for a placement."""

import sys

from collections import defaultdict

from os.path import splitext, basename

from six import iteritems

from rig.machine import Cores

from rig.place_and_route import allocate, route
from rig.place_and_route.utils import build_routing_tables

from rig.place_and_route.constraints import ReserveResourceConstraint

from rig.place_and_route.routing_tree import RoutingTree

import json

from netlist_to_json import json_to_netlist
from place import json_to_placements
from machine_to_json import json_to_machine


def measure_nets(netlist_name, vertices_resources, nets,
                 placement_algorithm, placement_duration, placements,
                 machine_name, machine):
    constraints = [ReserveResourceConstraint(Cores, slice(0, 2))]
    
    # Route the nets
    allocations = allocate(vertices_resources, nets, machine, constraints,
                           placements)
    routes = route(vertices_resources, nets, machine, constraints, placements,
                   allocations)
    
    routing_tables = build_routing_tables(routes,
                                          {n: (k, -1)
                                           for k, n in enumerate(nets)})
    
    # Standard columns
    std_header = "netlist,machine,placer,placement_duration"
    std_cols = "{},{},{},{}".format(netlist_name,
                                    machine_name,
                                    placement_algorithm,
                                    placement_duration)
    
    # Create per-net summary
    per_net_csv = "{},net,fan_out,total_hops\n".format(std_header)
    for net, routing_tree in iteritems(routes):
        index = nets.index(net)
        fan_out = len(net.sinks)
        total_hops = len(list(routing_tree))
        per_net_csv += "{},{},{},{}\n".format(std_cols,
                                              index,
                                              fan_out,
                                              total_hops)
    
    # Create per-chip summary
    per_chip_csv = "{},x,y,routing_table_entries,num_nets,total_weight\n".format(std_header)
    chip_num_nets = defaultdict(lambda: 0)
    chip_total_weight = defaultdict(lambda: 0.0)
    for net, routing_tree in iteritems(routes):
        for node in routing_tree:
            if isinstance(node, RoutingTree):
                chip_num_nets[node.chip] += 1
                chip_total_weight[node.chip] += net.weight
    for x, y in machine:
        routing_table_entries = len(routing_tables[(x, y)])
        per_chip_csv += "{},{},{},{},{},{}\n".format(std_cols,
                                               x, y,
                                               routing_table_entries,
                                               chip_num_nets[(x, y)],
                                               chip_total_weight[(x, y)])
    
    return (per_net_csv, per_chip_csv)


if __name__=="__main__":
    import sys
    if len(sys.argv) != 6:
        print("Expected five arguments: netlist placements machine per_net_stats per_chip_stats.")
        sys.exit(1)
    else:
        netlist_name = splitext(basename(sys.argv[1]))[0]
        with open(sys.argv[1], "r") as f:
            netlist = json_to_netlist(json.load(f))
        with open(sys.argv[2], "r") as f:
            placements = json_to_placements(json.load(f))
        machine_name = splitext(basename(sys.argv[3]))[0]
        with open(sys.argv[3], "r") as f:
            hostname, machine = json_to_machine(json.load(f))
        
        per_net_csv, per_chip_csv = \
            measure_nets(netlist_name,
                         netlist["vertices_resources"], netlist["nets"],
                         placements["algorithm"],
                         placements["placement_duration"],
                         placements["placements"],
                         machine_name, machine)
        
        with open(sys.argv[4], "w") as f:
            f.write(per_net_csv)
        with open(sys.argv[5], "w") as f:
            f.write(per_chip_csv)




