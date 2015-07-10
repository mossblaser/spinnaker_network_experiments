#!/usr/bin/env python

"""Run a single network experiment."""

import sys

from collections import defaultdict

from os.path import splitext, basename

from network_tester import Experiment, to_csv

from six import iteritems

import json

from netlist_to_json import json_to_netlist
from place import json_to_placements
from machine_to_json import json_to_machine


# The number of graduations in injection rate
NUM_STEPS = 30

def run_experiment(netlist_name, vertices_resources, nets,
                   placement_algorithm, placement_duration, placements,
                   machine_name, machine, hostname):
    e = Experiment(hostname)
    assert e.machine == machine
    
    vertices = defaultdict(e.new_vertex)
    
    # Make sure all vertices have a corresponding network tester vertex
    for vertex in vertices_resources:
        vertices[vertex]
    
    # Convert nets into network tester nets
    nets = [e.new_net(vertices[n.source],
                      [vertices[sink] for sink in n.sinks],
                      n.weight)
            for n in nets]
    
    e.placements = {vertices[v]: xy for v, xy in iteritems(placements)}
    
    max_weight = max(n.weight for n in nets)
    
    e.timestep = 1e-5
    
    e.warmup = 0.01
    e.duration = 0.1
    e.cooldown = 0.01
    
    e.record_sent = True
    e.record_blocked = True
    e.record_received = True
    
    e.record_local_multicast = True
    e.record_external_multicast = True
    e.record_dropped_multicast = True
    
    for reinject_packets in [False, True]:
        for step in range(NUM_STEPS):
            with e.new_group() as group:
                e.reinject_packets = reinject_packets
                
                # Probability per unit net weight
                probability = ((step + 1) / float(NUM_STEPS)) / max_weight
                for net in nets:
                    net.probability = probability * net.weight
                
                group.add_label("netlist", netlist_name)
                group.add_label("reinject_packets", e.reinject_packets)
                group.add_label("machine", machine_name)
                group.add_label("placer", placement_algorithm)
                group.add_label("placement_duration", placement_duration)
                group.add_label("injection_rate", (probability * max_weight) / e.timestep)
                group.add_label("duration", e.duration)
    
    results = e.run(ignore_deadline_errors=True)
    return (to_csv(results.totals()) + "\n",
            to_csv(results.router_counters()) + "\n")


if __name__=="__main__":
    import sys
    if len(sys.argv) != 6:
        print("Expected five arguments: netlist placements machine totals router_counters.")
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
        
        totals, router_counters = \
            run_experiment(netlist_name,
                           netlist["vertices_resources"], netlist["nets"],
                           placements["algorithm"],
                           placements["placement_duration"],
                           placements["placements"],
                           machine_name, machine, hostname)
        
        with open(sys.argv[4], "w") as f:
            f.write(totals)
        with open(sys.argv[5], "w") as f:
            f.write(router_counters)



