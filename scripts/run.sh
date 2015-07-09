#!/bin/bash

# This shell script places any netlists which are not yet placed and then runs
# experiments on all machines or just the machines specified on the
# commandline. Placements and experiments are not re-run unless the mahine or
# netlist has changed.

BASE_DIR="$(dirname "$0")/.."

SCRIPTS_DIR="$BASE_DIR/scripts"

NETLISTS_DIR="$BASE_DIR/netlists"
MACHINES_DIR="$BASE_DIR/machines"
PLACEMENTS_DIR="$BASE_DIR/placements"
RESULTS_DIR="$BASE_DIR/results"

# The set of Rig placement algorithms available
PLACERS=(hilbert sa)

# The set of netlists which exist
NETLISTS=($(for f in "$NETLISTS_DIR/"*.json; do basename "${f%.json}"; done))

# The set of machines. If non given on the CLI, run all known machines,
# otherwise, just those listed on the commandline will be used
ALL_MACHINES=($(for f in "$MACHINES_DIR/"*.json; do basename "${f%.json}"; done))
if [ -n "$*" ]; then
    MACHINES=("$@")
else
    MACHINES=("${ALL_MACHINES[@]}")
fi

for machine in "${MACHINES[@]}"; do
    if [ ! -f "$MACHINES_DIR/$machine.json" ]; then
        echo "ERROR: Unknown machine '$machine'" >&2
        exit 1
    fi
done

# Place any netlists which don't have placements (done in parallel)
echo "Placing netlists..."
parallel --ungroup -a <(
    for netlist in "${NETLISTS[@]}"; do
        for placer in "${PLACERS[@]}"; do
            for machine in "${MACHINES[@]}"; do
                netlist_file="$NETLISTS_DIR/$netlist.json"
                placement_file="$PLACEMENTS_DIR/$placer/$machine/$netlist.json"
                machine_file="$MACHINES_DIR/$machine.json"
                if [ ! -f "$placement_file" -o \
                     "$netlist_file" -nt "$placement_file" -o \
                     "$machine_file" -nt "$placement_file" ]; then
                    echo "echo \"  '$netlist' on '$machine' with '$placer'\"; \
                          mkdir -p \"$(dirname "$placement_file")\"; \
                          python \"$SCRIPTS_DIR/place.py\" \
                                 \"$netlist_file\" \"$machine_file\" \
                                 \"$placer\" > \"$placement_file\";"
                fi
            done
        done
    done) \
    {}

# Run any experiments which haven't been run (done serially)
echo "Running experiments..."
for netlist in "${NETLISTS[@]}"; do
    for placer in "${PLACERS[@]}"; do
        for machine in "${MACHINES[@]}"; do
            netlist_file="$NETLISTS_DIR/$netlist.json"
            placement_file="$PLACEMENTS_DIR/$placer/$machine/$netlist.json"
            machine_file="$MACHINES_DIR/$machine.json"
            totals_file="$RESULTS_DIR/totals/$placer/$machine/$netlist.csv"
            router_counters_file="$RESULTS_DIR/router_counters/$placer/$machine/$netlist.csv"
            if [ ! -f "$totals_file" -o \
                 ! -f "$router_counters_file" -o \
                 "$placement_file" -nt "$totals_file" -o \
                 "$placement_file" -nt "$router_counters_file" ]; then
                echo "  '$netlist' on '$machine' with '$placer'";
                
                mkdir -p "$(dirname "$totals_file")"
                mkdir -p "$(dirname "$router_counters_file")"
                
                python "$SCRIPTS_DIR/experiment.py" \
                       "$netlist_file" "$placement_file" "$machine_file" \
                       "$totals_file" "$router_counters_file"
            fi
        done
    done
done

# Merge results files
echo "Merging results..."
global_totals_file="$RESULTS_DIR/totals.csv"
global_router_counters_file="$RESULTS_DIR/router_counters.csv"
[ -f "$global_totals_file" ] && rm "$global_totals_file"
[ -f "$global_router_counters_file" ] && rm "$global_router_counters_file"
first=""
for netlist in "${NETLISTS[@]}"; do
    for placer in "${PLACERS[@]}"; do
        for machine in "${ALL_MACHINES[@]}"; do
            totals_file="$RESULTS_DIR/totals/$placer/$machine/$netlist.csv"
            router_counters_file="$RESULTS_DIR/router_counters/$placer/$machine/$netlist.csv"
            # Skip experiments which don't exist
            if [ ! -f "$totals_file" -o ! -f "$router_counters_file" ]; then
                continue
            fi
            
            if [ -z "$first" ]; then
                # Only the first file will have the CSV heading kept
                first=false
                cp "$totals_file" "$global_totals_file"
                cp "$router_counters_file" "$global_router_counters_file"
            else
                # All other files will have their headers stripped
                tail -n+2 "$totals_file" >> "$global_totals_file"
                tail -n+2 "$router_counters_file" >> "$global_router_counters_file"
            fi
        done
    done
done
