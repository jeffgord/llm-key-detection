#!/bin/bash
#SBATCH --job-name=lvcr-predict-gtzan
#SBATCH --account=torch_pr_932_general
#SBATCH --cpus-per-task=16
#SBATCH --mem=64GB
#SBATCH --time=04:00:00
#SBATCH --output=lvcr-predict-gtzan.log
#SBATCH --error=lvcr-predict-gtzan.log

set -euo pipefail

REPO_ROOT=${SCRATCH}/llm-key-estimation

IMAGE=/share/apps/images/cuda12.1.1-cudnn8.9.0-devel-ubuntu22.04.2.sif
OVERLAY=${REPO_ROOT}/conda-overlay.ext3:rw

DATA_DIR=${DATA_DIR:-gtzan-key/audio}
OUTPUT_DIR=${OUTPUT_DIR:-chords/raw-gtzan}
NUM_WORKERS=${NUM_WORKERS:-${SLURM_CPUS_PER_TASK:-16}}

export DATA_DIR OUTPUT_DIR NUM_WORKERS

cd "${REPO_ROOT}"

echo "Job ID: ${SLURM_JOB_ID:-unknown}"
echo "Node(s): ${SLURM_NODELIST:-unknown}"
echo "Working directory: $(pwd)"
echo "Data dir: ${DATA_DIR}"
echo "Output dir: ${OUTPUT_DIR}"
echo "Workers: ${NUM_WORKERS}"

singularity exec --fakeroot --nv --overlay "${OVERLAY}" "${IMAGE}" /bin/bash -lc '
  cd "'"${REPO_ROOT}"'"
  source /ext3/env.sh
  python chord-recognition/lvcr_predict.py \
    --data-dir "${DATA_DIR}" \
    --output-dir "${OUTPUT_DIR}" \
    --num-workers "${NUM_WORKERS}"
'
