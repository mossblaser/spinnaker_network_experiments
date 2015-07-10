NETLIST="$1"; shift
MACHINE="$1"; shift
PLACER="$1"; shift

BASE_DIR="$(dirname "$0")/.."
SCRIPTS_DIR="$BASE_DIR/scripts"

TMP_FILE="$(mktemp)"

python scripts/json_to_netlist.py \
    "netlists/$NETLIST.json" \
    "machines/$MACHINE.json" \
    "placements/$PLACER/$MACHINE/$NETLIST.json" \
    "$TMP_FILE"

rig-par-diagram "$TMP_FILE" "$@"

rm "$TMP_FILE"
