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
# slugs reads its own format: the compiler of slugs translates the file of dsl_tool
COMPILER=${SLUGSCOMPILER:-$SLUGS/tools/StructuredSlugsParser/compiler.py}

clear && echo -n "$> dsl_tool -i template_0_unrealizable.txt -o $WD/unrealizable"
read ans
dsl_tool -i template_0_unrealizable.txt -o $WD/unrealizable
python3 $COMPILER $WD/unrealizable.structuredSlugs > $WD/unrealizable.slugsin
slugs $WD/unrealizable.slugsin
read ans
echo
echo

echo -n "$> dsl_tool -i template_0_realizable.txt -o $WD/realizable"
read ans
dsl_tool -i template_0_realizable.txt -o $WD/realizable
python3 $COMPILER $WD/realizable.structuredSlugs > $WD/realizable.slugsin
slugs $WD/realizable.slugsin
slugs --explicitStrategy --jsonOutput $WD/realizable.slugsin > $WD/EPS.json
less $WD/EPS.json
