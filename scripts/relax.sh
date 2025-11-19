#!/bin/bash
#SBATCH -J relax_array
#SBATCH --output=relax_slurm/relax__%A_%a.out
#SBATCH --error=relax_slurm/relax__%A_%a.err
#SBATCH -N 1
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH -p htc
#SBATCH -q public
#SBATCH --array=1-{# of inputs}

echo "=== SLURM JOB START ==="
echo "Node: $(hostname)"
echo "Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Date: $(date)"
echo "---------------------------"

# ============================================================
# USER SETTINGS
# ============================================================
ROSETTA_BIN="/scratch/{USER}/rosetta.source.release-371/main/source/bin/relax.linuxgccrelease"

INPUT_DIR="/scratch/{USER}/alphafold/pdbs_unrelaxed"   
OUT_DIR="/scratch/{USER}/alphafold/relaxed"

mkdir -p "$OUT_DIR" "$OUT_DIR/logs"

# ============================================================
# BUILD FILE LIST (once)
# ============================================================

FILE_LIST="$OUT_DIR/pdb_list.txt"

# Only generate list if it doesn't already exist
if [[ ! -f "$FILE_LIST" ]]; then
    echo "Building list of PDBs from: $INPUT_DIR"
    find "$INPUT_DIR" -maxdepth 1 -type f -name "*.pdb" | sort > "$FILE_LIST"
    echo "Found $(wc -l < "$FILE_LIST") PDBs."
fi

NUM_FILES=$(wc -l < "$FILE_LIST")

# Stop extra array tasks
if [[ $SLURM_ARRAY_TASK_ID -ge $NUM_FILES ]]; then
    echo "Task ${SLURM_ARRAY_TASK_ID} has no input (only $NUM_FILES files) — exiting."
    exit 0
fi

# ============================================================
# GET THIS TASK'S FILE
# ============================================================

PDB_PATH=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$FILE_LIST")

if [[ -z "$PDB_PATH" ]]; then
    echo "No PDB path for task ${SLURM_ARRAY_TASK_ID} — skipping."
    exit 0
fi

BASE=$(basename "$PDB_PATH" .pdb)
LOG_FILE="${OUT_DIR}/logs/${BASE}_relax.log"

echo "Processing: $BASE"
echo "Input: $PDB_PATH"
echo "Output dir: $OUT_DIR"
echo "Log: $LOG_FILE"

# ============================================================
# SKIP if already relaxed
# ============================================================

if [[ -f "${OUT_DIR}/${BASE}_relaxed_0001.pdb" ]]; then
    echo "Already relaxed — skipping."
    exit 0
fi

# ============================================================
# RUN RELAX
# ============================================================

"$ROSETTA_BIN" \
    -s "$PDB_PATH" \
    -relax:default_repeats 1 \
    -nstruct 1 \
    -out:suffix _relaxed \
    -out:path:all "$OUT_DIR" \
    > "$LOG_FILE" 2>&1

STATUS=$?

if [[ $STATUS -eq 0 ]]; then
    echo "Done: $BASE"
else
    echo "Relax failed for $BASE (check log)"
fi

echo "Finished at: $(date)"

