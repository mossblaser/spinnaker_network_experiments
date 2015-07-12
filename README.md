SpiNNaker Place-and-Route Network Experiments
=============================================

This repository contains infrastructure and data files for running comparative
studies of the impact of place-and-route software on SpiNNaker network
performance.

By running `scripts/run.sh`, netlists placed in the [`netlists`](./netlists/)
directory are placed using all available algorithms onto the SpiNNaker machiens
defined in [`machines`](./machines/) and the resulting palcements are dumped in
[`placements`](./placements/). These placed netlists are then modelled using
[`network_tester`](https://github.com/project-rig/network_tester) on SpiNNaker
and the results are collated in [`results`](./results/).

See the README files in each of these directories for details of the file
formats required in each.

Quick-Start
-----------

Install dependencies of Python utility scripts:

	$ pip install -r requirements.txt

Netlists dumped by `nengo_spinnaker` and similar can be converted using:

	$ python scripts/netlist_to_json.py netlist > netlists/my_netlist_name.json

Synthetic netlists can also be generated using:

	$ python scripts/generate_synthetic_benchmark.py ... > netlists/my_netlist_name.json

See `python scripts/generate_synthetic_benchmark.py --help` for more details.

A standard set of synthetic netlists can be generated using:

	$ ./scripts/generate_standard_netlists.sh

Generate a machine description file for any available machines which are to be
used:

	$ python scripts/machine_to_json.py HOSTNAME > machines/my_machine_name.json

Place and run any new/modified netlists and collect the results:

	$ # Run placement and static analysis only
	$ ./scripts/run.sh
	$ # OR: As above but also run experiments on the specified set of machines
	$ ./scripts/run.sh my_machine_name my_other_machine_name
