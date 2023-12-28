#!/bin/sh

WD=$1

if test "$#" -ne 1; then
    echo "One parameters required: 1. working directory"
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


less requirements.txt

less template_0_unrealizable.txt
clear && echo -n "$> dsl_tool -i template_0_unrealizable.txt -o $WD/unrealizable.structuredSlugs"
read ans
dsl_tool -i template_0_unrealizable.txt -o $WD/unrealizable.spc -b gr1c
gr1c -r $WD/unrealizable.spc
read ans
echo
echo

echo -n "$> dsl_tool -i template_0_realizable.txt -o $WD/realizable.structuredSlugs"
read ans
dsl_tool -i template_0_realizable.txt -o $WD/realizable.spc -b gr1c
gr1c -r $WD/realizable.spc
gr1c $WD/realizable.spc &> $WD/EPS.json | less

gr1c -t dot $WD/realizable.spc > $WD/EPS.dot
dot -Tpdf $WD/EPS.dot > $WD/EPS.pdf

