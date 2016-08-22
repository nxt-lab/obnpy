#!/bin/bash

# need to set obnchai and smnchai aliases before using them
shopt -s expand_aliases
source ~/.bash_profile

echo "Starting python OBN interface test"
echo "running chaiscript node..."
obnchai othernode.ons &
echo "run python node..."
python extnode.py &
echo "running simulation manager node..."
smnchai testpy.oss
echo "test finished"
