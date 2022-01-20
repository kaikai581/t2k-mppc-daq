#!/bin/bash

# decorate the command line
if [[ $EUID -ne 0 ]]; then
    PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\n\$\[\033[00m\] '
else
    PS1='\[\033[01;31m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\n\$\[\033[00m\] '
fi

# my own frequently used aliases
alias ll='ls -l --color=auto'

# enable conda
if [ "$HOSTNAME" = hepr2021-Precision-5820-Tower-X-Series ]; then
    . /home/hepr2021/anaconda3/etc/profile.d/conda.sh
else
    . /home/hepr2018/sklin/anaconda3/etc/profile.d/conda.sh
fi

# activate environment
conda activate root6

# quiet down the warning
export XDG_RUNTIME_DIR=/tmp/runtime-root

# avoid generation of .pyc files
export PYTHONDONTWRITEBYTECODE=1

# unalias root to make sure the anaconda ROOT package is used
unalias root 2>/dev/null
