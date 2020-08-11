#!/bin/bash

# enable conda
. /home/hepr2018/sklin/anaconda3/etc/profile.d/conda.sh

# activate environment
conda activate mppc-daq

# quiet down the warning
export XDG_RUNTIME_DIR=/tmp/runtime-root

# avoid generation of .pyc files
export PYTHONDONTWRITEBYTECODE=1

# run the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
python $DIR/main_control.py
