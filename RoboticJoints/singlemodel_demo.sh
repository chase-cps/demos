#!/bin/sh

SLUGSCOMPILER=$1
WD=$2

if test "$#" -ne 2; then
    echo "Two parameters required: 1. slugs compiler path, and 2. working directory"
    exit
fi 

mkdir -p $WD 

PS1="SINGLE MODEL DEMO >> " 
clear

red () {
    echo "\033[0;31m$1"
}

redn () {
    echo -n "\033[0;31m$1"
}

black () {
    echo "\033[0m$1"
}

blackn () {
    echo -n "\033[0m$1"
}


less single_model.ltl
clear && echo -n "SINGLE MODEL DEMO >> logics_tool -i single_model.ltl -o $WD -c singlemodel.chase"
read ans
logics_tool -i single_model.ltl -o $WD -c singlemodel.chase -V
python3 $SLUGSCOMPILER \
    $WD/single_model.structuredSlugs > $WD/single_model.slugsin
    slugs --explicitStrategy $WD/single_model.slugsin > $WD/single_mode.fsm
