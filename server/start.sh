#!/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate shapez2
exec uvicorn webapp:app --host 127.0.0.1 --port 8000 --reload