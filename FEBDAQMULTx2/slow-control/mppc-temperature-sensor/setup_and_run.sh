#!/bin/bash

# Check if a process is running already.
# If yes, kill it before proceed.
# Source: https://stackoverflow.com/questions/3510673/find-and-kill-a-process-in-one-line-using-bash-and-regex
# Below will result in warning if no process exists.
# kill -9 $(ps aux | grep '[m]ain_control.py' | awk '{print $2}')
ps aux | grep '[m]ain_control.py' | awk '{print $2}' | xargs -I{} kill -9 {}

# enable conda
if [ "$HOSTNAME" = hepr2021-Precision-5820-Tower-X-Series ]; then
    . /home/hepr2021/anaconda3/etc/profile.d/conda.sh
    # activate environment
    conda activate root6
else
    . /home/hepr2018/sklin/anaconda3/etc/profile.d/conda.sh
    # activate environment
    conda activate mppc-daq
fi

# quiet down the warning
mkdir -p /tmp/runtime-root
export XDG_RUNTIME_DIR=/tmp/runtime-root

# avoid generation of .pyc files
export PYTHONDONTWRITEBYTECODE=1

# run the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
jupyter-notebook --allow-root
