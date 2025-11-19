#!/bin/bash
#SBATCH --job-name=alphafold3_array
#SBATCH --output=alphafold_slurm/alphafold3_%A_%a.out
#SBATCH --error=alphafold_slurm/alphafold3_%A_%a.err
#SBATCH --array=1-{# of inputs}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --partition=htc
#SBATCH --qos=public
#SBATCH --gres=gpu:1
#SBATCH --time=01:30:00
#SBATCH --export=NONE

# Load CUDA (must match container build)
module load cuda-12.6.1-gcc-12.1.0

# Paths
SIMG=/packages/apps/simg/alphafold-3.0.0.sif
AF3_INPUT_DIR=/scratch/{USER}/alphafold/af_inputs
AF3_OUTPUT_DIR=/scratch/{USER}/alphafold/af_outputs
MODEL_DIR=/scratch/ggrama/alphafold3/params #or I can share the parameters with you
DB_DIR=/scratch/ggrama/alphafold3/af3_database

mkdir -p $AF3_OUTPUT_DIR/logs

# Select JSON for this array task
INPUT_JSON=$(ls $AF3_INPUT_DIR/*.json | sed -n "${SLURM_ARRAY_TASK_ID}p")
if [ -z "$INPUT_JSON" ]; then
    echo "No JSON file found for SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID"
    exit 1
fi

echo "Running AlphaFold 3 on $INPUT_JSON"

# Run AlphaFold 3 inside Apptainer
exec /usr/bin/apptainer exec --nv \
    -B /scratch/$USER:/scratch/$USER \
    $SIMG \
    /bin/bash -c "
        python /app/alphafold/run_alphafold.py \
            --json_path=$INPUT_JSON \
            --model_dir=$MODEL_DIR \
            --db_dir=$DB_DIR \
            --output_dir=$AF3_OUTPUT_DIR
    "

