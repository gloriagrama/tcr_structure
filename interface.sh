#!/bin/bash
#SBATCH --job-name=interface_array
#SBATCH --array=0-7200
#SBATCH --output=interface_slurm/%x_%A_%a.out
#SBATCH --error=interface_slurm/%x_%A_%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --partition=htc
#SBATCH --qos=public
#SBATCH --time=0:15:00
#SBATCH --export=NONE

echo "=== SLURM JOB START ==="
echo "Node: $(hostname)"
echo "Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "---------------------------"

# === Environment ===
export ROSETTA_BIN="/scratch/ggrama/rosetta.source.release-371/main/source/bin"
export PATH="$ROSETTA_BIN:$PATH"

# === Input/output directories ===
FINAL_DIR="/scratch/ggrama/recomb/generated/interface_pdbs"
SCORES_DIR="/scratch/ggrama/recomb/generated/interface_scores"
LOGS_DIR="/scratch/ggrama/recomb/generated/interface_logs"

mkdir -p "$SCORES_DIR" "$LOGS_DIR" interface_slurm

# === NEW: Directly read PDBs from directory (NO LIST NEEDED) ===
mapfile -t PDBS < <(find "$FINAL_DIR" -maxdepth 1 -type f -name "*.pdb" | sort)

NUM_FILES=${#PDBS[@]}

if [[ $SLURM_ARRAY_TASK_ID -ge $NUM_FILES ]]; then
    echo "⚠️ No file for index ${SLURM_ARRAY_TASK_ID} (only $NUM_FILES files)"
    exit 0
fi

PDB_PATH="${PDBS[$SLURM_ARRAY_TASK_ID]}"
BASE=$(basename "$PDB_PATH" .pdb)

SCORE_OUT="${SCORES_DIR}/${BASE}_scores.sc"
LOG_OUT="${LOGS_DIR}/${BASE}.log"

# === Skip if already scored ===
if [[ -f "$SCORE_OUT" ]]; then
    echo "⏩ Already scored: $BASE"
    exit 0
fi

# === Check existence ===
if [[ ! -f "$PDB_PATH" ]]; then
    echo "❌ PDB not found: $PDB_PATH"
    exit 1
fi

echo "Running InterfaceAnalyzer on: $PDB_PATH"
echo "Score output: $SCORE_OUT"
echo "Log output:   $LOG_OUT"

# === Run Rosetta InterfaceAnalyzer ===
"$ROSETTA_BIN/InterfaceAnalyzer.linuxgccrelease" \
    -s "$PDB_PATH" \
    -interface A_B \
    -ignore_unrecognized_res \
    -pack_separated \
    -nstruct 1 \
    -out:file:scorefile "$SCORE_OUT" \
    -out:path:all "$SCORES_DIR" \
    > "$LOG_OUT" 2>&1

if [[ $? -eq 0 ]]; then
    echo "✅ Finished successfully: $BASE"
else
    echo "❌ InterfaceAnalyzer failed: $BASE (check log)"
fi

echo "=== JOB DONE ==="

