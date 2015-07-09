#!/usr/bin/env python

"""Generate a JSON machine description of a SpiNNaker system."""

import json

from six import iteritems

from rig.machine_control import MachineController

from rig.machine import Machine, Cores, SDRAM, SRAM, Links


def _resources_to_json(resources):
    return {str(r): v for r, v in iteritems(resources)}


def machine_to_json(hostname):
    """Represent the resources available in a given machine as a JSON
    object."""
    machine = MachineController(hostname).get_machine()
    
    return {"hostname": hostname,
            "width": machine.width,
            "height": machine.height,
            "chip_resources":
                _resources_to_json(machine.chip_resources),
            "chip_resource_exceptions": [
                [x, y, _resources_to_json(r)]
                for (x, y), r in
                iteritems(machine.chip_resource_exceptions)
            ],
            "dead_chips": [[x, y] for x, y in machine.dead_chips],
            "dead_links": [[x, y, int(link)]
                           for x, y, link in machine.dead_links],
           }


def json_to_machine(json_machine):
    """Return the hostname and Machine object for a supplied machine unpacked
    from JSON."""
    standard_resources = {
        "Cores": Cores,
        "SDRAM": SDRAM,
        "SRAM": SRAM,
    }
    
    machine = Machine(json_machine["width"],
                      json_machine["height"],
                      {standard_resources.get(r, r): v
                       for r, v in iteritems(json_machine["chip_resources"])},
                      {(x, y): {standard_resources.get(r, r): v
                        for r, v in iteritems(resources)}
                       for x, y, resources in
                       json_machine["chip_resource_exceptions"]},
                      set((x, y) for x, y in json_machine["dead_chips"]),
                      set((x, y, Links(l))
                          for x, y, l in json_machine["dead_links"]))
    return (json_machine["hostname"], machine)


if __name__=="__main__":
    import sys
    if len(sys.argv) != 2:
        print("Expected one argument: hostname.")
        sys.exit(1)
    else:
        print(json.dumps(machine_to_json(sys.argv[1])))

