#!/bin/bash

# decorate the command line
PS1='\[\033[01;31m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\n\$\[\033[00m\] '

# enable conda
. /home/hepr2018/sklin/anaconda3/etc/profile.d/conda.sh

# activate environment
conda activate root6

# quiet down the warning
export XDG_RUNTIME_DIR=/tmp/runtime-root

# avoid generation of .pyc files
export PYTHONDONTWRITEBYTECODE=1