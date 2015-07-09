#!/usr/bin/env python

"""Generates netlists for synthetic benchmark networks."""

import argparse

import json

import re

from rig.machine import Cores

from rig.netlist import Net

from math import sqrt, ceil

import random

from six import iteritems

from netlist_to_json import netlist_to_json

def to_dist(description):
    # XXX: Insecure, but for expert use only!
    local_vars = {n: getattr(random, n) for n in dir(random)}
    return (lambda: eval(description, local_vars))


def add_random_net_per_vertex(vertices, nets, probability, num_sinks="1", weight="1"):
    num_sinks_dist = to_dist(num_sinks)
    weight_dist = to_dist(weight)
    
    for vertex in vertices:
        nets.append(Net(vertex,
                        random.sample(vertices, int(num_sinks_dist())),
                        float(weight_dist())))


def add_nearest_neighbour(vertices, nets, topology, weight="1"):
    weight_dist = to_dist(weight)
    
    wraps = topology.endswith("torus")
    
    neighbour_vectors = [
        (+1, +0),
        (-1, +0),
        (+0, +1),
        (+0, -1),
    ]
    if topology.startswith("hex"):
        neighbour_vectors.extend([
            (+1, +1),
            (-1, -1),
        ])
    
    width = int(ceil(sqrt(len(vertices))))
    positions = {(n % width, n // width): v for n, v in enumerate(vertices)}
    
    for (x, y), vertex in iteritems(positions):
        neighbours = []
        for (dx, dy) in neighbour_vectors:
            xx = x + dx
            yy = y + dy
            if wraps:
                xx %= width
                yy %= width
            neighbour = positions.get((xx, yy), None)
            if neighbour is not None:
                neighbours.append(neighbour)
        nets.append(Net(vertex, neighbours, weight_dist()))


def add_distance_dependent(vertices, nets, topology,
                           num_sinks="1", dx="0", dy=None, weight="1"):
    num_sinks_dist = to_dist(num_sinks)
    dx_dist = to_dist(dx)
    dy_dist = to_dist(dy if dy is not None else dx)
    weight_dist = to_dist(weight)
    
    wraps = topology.endswith("torus")
    
    width = int(ceil(sqrt(len(vertices))))
    positions = {(n % width, n // width): v for n, v in enumerate(vertices)}
    
    for (x, y), vertex in iteritems(positions):
        neighbours = []
        for _ in range(int(num_sinks_dist())):
            xx = x + dx_dist()
            yy = y + dy_dist()
            if wraps:
                xx %= width
                yy %= width
            xx = int(round(xx))
            yy = int(round(yy))
            neighbour = positions.get((xx, yy), None)
            if neighbour is not None and neighbour not in neighbours:
                neighbours.append(neighbour)
        if neighbours:
            nets.append(Net(vertex, neighbours, weight_dist()))


def add_all_to_all_pipeline(vertices, nets, width, weight="1"):
    weight_dist = to_dist(weight)
    
    n_vertices = len(vertices)
    width = int(width)
    nets += [Net(vertices[i],
                 vertices[(i//width + 1)*width: (i//width + 2)*width],
                 weight_dist())
             for i in range(n_vertices)
             if i + width < n_vertices]

def add_merge_node_pipeline(vertices, nets, width, weight="1"):
    weight_dist = to_dist(weight)
    
    n_vertices = len(vertices)
    width = int(width)
    vertex_iter = iter(vertices)
    last_node = None
    try:
        while True:
            node = next(vertex_iter)
            if last_node is not None:
                nets.append(Net(last_node, node, weight_dist()))
            
            ensemble_array = []
            try:
                for _ in range(width):
                    ensemble_array.append(next(vertex_iter))
            except StopIteration:
                pass
            nets.append(Net(node, ensemble_array, weight_dist()))
            
            last_node = next(vertex_iter)
            for v in ensemble_array:
                nets.append(Net(v, last_node, weight_dist()))
    except StopIteration:
        pass


def main(argv):
    parser = argparse.ArgumentParser(
        description="Generate a synthetic benchmark network.")
    
    parser.add_argument("num_vertices", metavar="NUM_VERTICES", type=int,
                        help="Specifies the number of vertices in the "
                             "benchmark.")
    
    parser.add_argument("--random-net-per-vertex", "-r",
                        metavar=("PROBABILITY",
                                 "NUM_SINKS, WEIGHT"),
                        nargs="+", action="append", default=[],
                        help="Add a net from each vertex with PROBABILITY "
                             "going to NUM_SINKS sinks and with weight "
                             "WEIGHT. NUM_SINKS and WEIGHT default to 1 but "
                             "can be a constant or some random distribution.")
    
    parser.add_argument("--nearest-neighbour", "-n",
                        metavar=("{2Dmesh,2Dtorus,hexmesh,hextorus}",
                                 "WEIGHT"),
                        nargs="+", action="append", default=[],
                        help="Add a net from each vertex to its immediate "
                             "neighbours, presuming a square-ish topology "
                             "of the specified type.")
    
    parser.add_argument("--distance-dependent", "-d",
                        metavar=("{2Dmesh,2Dtorus}",
                                 "NUM_SINKS, DX, DY, WEIGHT"),
                        nargs="+", action="append", default=[],
                        help="Adds a net to each vertex which connects to "
                             "(up to) NUM_SINKS vertices which are selected "
                             "by adding DX and DY to the coordinates of the "
                             "vertex.")
    
    parser.add_argument("--all-to-all-pipeline", "-p",
                        metavar=("WIDTH", "WEIGHT"),
                        nargs="+", action="append", default=[],
                        help="Divide the nets into a series of groups of "
                             "WIDTH vertices with each group being "
                             "all-to-all connected to the vertices in next "
                             "group with weight WEIGHT.")
    
    parser.add_argument("--merge-node-pipeline", "-P",
                        metavar=("WIDTH", "WEIGHT"),
                        nargs="+", action="append", default=[],
                        help="Divide the nets into a series of groups of "
                             "WIDTH vertices. Each group's vertices sink "
                             "exactly one node (not part of any group) which "
                             "tnen sinks another independent node which then "
                             "sinks all the vertices in the next group. "
                             "This approximately matches a style of network "
                             "generated by nengo_spinnaker.")
    
    args = parser.parse_args(argv)
    
    # Create the specified number of vertices
    vertices = [str(i + 1) for i in range(args.num_vertices)]
    vertices_resources = {v: {Cores: 1} for v in vertices}
    
    nets = []
    
    # Add connectivity according to arguments
    for a in args.random_net_per_vertex:
        add_random_net_per_vertex(vertices, nets, *a)
    for a in args.nearest_neighbour:
        add_nearest_neighbour(vertices, nets, *a)
    for a in args.distance_dependent:
        add_distance_dependent(vertices, nets, *a)
    for a in args.all_to_all_pipeline:
        add_all_to_all_pipeline(vertices, nets, *a)
    for a in args.merge_node_pipeline:
        add_merge_node_pipeline(vertices, nets, *a)
    
    # Dump the netlist as a file
    json_netlist = netlist_to_json({
        "vertices_resources": vertices_resources,
        "nets": nets,
    })
    json_netlist["generator_arguments"] = " ".join(argv)
    print(json.dumps(json_netlist))
    return 0


if __name__=="__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
