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
PLACERS=(hilbert sa rand)

# The set of netlists which exist
NETLISTS=($(for f in "$NETLISTS_DIR/"*.json; do basename "${f%.json}"; done))

# The set of all defined machines.
ALL_MACHINES=($(for f in "$MACHINES_DIR/"*.json; do basename "${f%.json}"; done))

# The set of machines to run
MACHINES=("$@")

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
            for machine in "${ALL_MACHINES[@]}"; do
                netlist_file="$NETLISTS_DIR/$netlist.json"
                placement_file="$PLACEMENTS_DIR/$placer/$machine/$netlist.json"
                skip_placement_file="$PLACEMENTS_DIR/$placer/$machine/$netlist.skip"
                machine_file="$MACHINES_DIR/$machine.json"
                placement_script="$SCRIPTS_DIR/place.py"
                temp_file="$(mktemp)"
                if [ \( ! -f "$placement_file" -o \
                        "$placement_script" -nt "$placement_file" -o \
                        "$netlist_file" -nt "$placement_file" -o \
                        "$machine_file" -nt "$placement_file" \) -a \
                     \( ! -f "$skip_placement_file" -o \
                        "$placement_script" -nt "$skip_placement_file" -o \
                        "$netlist_file" -nt "$skip_placement_file" -o \
                        "$machine_file" -nt "$skip_placement_file" \) ]; then
                    echo "echo \"  '$netlist' on '$machine' with '$placer'\"; \
                          [ -f \"$skip_placement_file\" ] && rm \"$skip_placement_file\"; \
                          mkdir -p \"$(dirname "$placement_file")\"; \
                          python \"$SCRIPTS_DIR/place.py\" \
                                 \"$netlist_file\" \"$machine_file\" \
                                 \"$placer\" > \"$temp_file\" \
                          && mv \"$temp_file\" \"$placement_file\" \
                          || ( [ \"$?\" = \"10\" ] && touch \"$skip_placement_file\"; \
                               rm \"$temp_file\"; )"
                fi
            done
        done
    done) \
    {}


# Calcualte stats for all netlists
echo "Statically analysing placed netlists..."
parallel --ungroup -a <(
    for netlist in "${NETLISTS[@]}"; do
        for placer in "${PLACERS[@]}"; do
            for machine in "${ALL_MACHINES[@]}"; do
                netlist_file="$NETLISTS_DIR/$netlist.json"
                placement_file="$PLACEMENTS_DIR/$placer/$machine/$netlist.json"
                machine_file="$MACHINES_DIR/$machine.json"
                stats_script="$SCRIPTS_DIR/static_analysis.py"
                net_stats_file="$RESULTS_DIR/net_stats/$placer/$machine/$netlist.csv"
                chip_stats_file="$RESULTS_DIR/chip_stats/$placer/$machine/$netlist.csv"
                # Skip experiments without any placement available
                if [ ! -f "$placement_file" ]; then
                    continue
                fi
                
                # Re-run stats if results missing/out-of-date
                if [ ! -f "$net_stats_file" -o \
                     ! -f "$chip_stats_file" -o \
                     "$stats_script" -nt "$net_stats_file" -o \
                     "$stats_script" -nt "$chip_stats_file" -o \
                     "$placement_file" -nt "$net_stats_file" -o \
                     "$placement_file" -nt "$chip_stats_file" ]; then
                    
                    echo "echo \"  '$netlist' on '$machine' with '$placer'\";\
                          mkdir -p \"$(dirname "$net_stats_file")\"; \
                          mkdir -p \"$(dirname "$chip_stats_file")\"; \
                          python \"$stats_script\" \
                                 \"$netlist_file\" \"$placement_file\" \
                                 \"$machine_file\" \
                                 \"$net_stats_file\" \"$chip_stats_file\";"
                fi
            done
        done
    done) \
    {}

# Run any experiments which haven't been run (done serially)
echo "Running experiments on ${#MACHINES[@]} machines..."
dead_machines=()
for netlist in "${NETLISTS[@]}"; do
    for placer in "${PLACERS[@]}"; do
        for machine in "${MACHINES[@]}"; do
            netlist_file="$NETLISTS_DIR/$netlist.json"
            placement_file="$PLACEMENTS_DIR/$placer/$machine/$netlist.json"
            machine_file="$MACHINES_DIR/$machine.json"
            experiment_script="$SCRIPTS_DIR/experiment.py"
            totals_file="$RESULTS_DIR/totals/$placer/$machine/$netlist.csv"
            router_counters_file="$RESULTS_DIR/router_counters/$placer/$machine/$netlist.csv"
            net_stats_file="$RESULTS_DIR/net_stats/$placer/$machine/$netlist.csv"
            chip_stats_file="$RESULTS_DIR/chip_stats/$placer/$machine/$netlist.csv"
            # Skip experiments without any placement available
            if [ ! -f "$placement_file" ]; then
                continue
            fi
            
            # If the machine involved has failed, don't bother trying to use it
            # again...
            is_dead=""
            for dead_machine in "${dead_machines[@]}"; do
                if [ "$dead_machine" = "$machine" ]; then
                    is_dead="True"
                fi
            done
            if [ -n "$is_dead" ]; then
                continue
            fi
            
            
            # Re-run experiment on machine if results missing/out-of-date
            if [ ! -f "$totals_file" -o \
                 ! -f "$router_counters_file" -o \
                 "$experiment_script" -nt "$totals_file" -o \
                 "$experiment_script" -nt "$router_counters_file" -o \
                 "$placement_file" -nt "$totals_file" -o \
                 "$placement_file" -nt "$router_counters_file" ]; then
                echo "  '$netlist' on '$machine' with '$placer'";
                
                mkdir -p "$(dirname "$totals_file")"
                mkdir -p "$(dirname "$router_counters_file")"
                
                python "$experiment_script" \
                       "$netlist_file" "$placement_file" "$machine_file" \
                       "$totals_file" "$router_counters_file" \
                    || dead_machines=("${dead_machines[@]}" "$machine")
            fi
        done
    done
done

# Merge results files
echo "Merging results..."
RESULT_FILES=("totals" "router_counters" "net_stats" "chip_stats")
for file in "${RESULT_FILES[@]}"; do
    [ -f "$RESULTS_DIR/$file.csv" ] && rm "$RESULTS_DIR/$file.csv" 
done
for netlist in "${NETLISTS[@]}"; do
    for placer in "${PLACERS[@]}"; do
        for machine in "${ALL_MACHINES[@]}"; do
            for file in "${RESULT_FILES[@]}"; do
                global_file="$RESULTS_DIR/$file.csv"
                specific_file="$RESULTS_DIR/$file/$placer/$machine/$netlist.csv"
                # Skip experiments which don't exist
                if [ ! -f "$specific_file" ]; then
                    continue
                fi
                
                if [ ! -f "$global_file" ]; then
                    # Only the first file will have the CSV heading kept
                    cp "$specific_file" "$global_file"
                else
                    # All other files will have their headers stripped
                    tail -n+2 "$specific_file" >> "$global_file"
                fi
            done
        done
    done
done
