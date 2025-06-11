#!/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate shapez2
exec uvicorn webapp:app --host 0.0.0.0 --port 8000 --reload --log-config logging_config.yaml