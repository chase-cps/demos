#!/bin/sh

WD=$1

if test "$#" -ne 1; then
    echo "One parameters required: working directory"
    exit
fi

mkdir -p $WD 

PS1="COMPOSITIONAL MODEL DEMO >> "
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

less specs.ltl
clear && red "Verification of the refinement relation"
blackn "COMPOSITIONAL MODEL DEMO >> logics_tool -i specs.ltl -o $WD -c verification.chase"
read ans

logics_tool -i specs.ltl -o $WD -c verification.chase -V

red "Run NuSMV to verify refinement"
ref=`nuxmv $WD/refinement.smv | egrep "is true" | wc -l `

if test $ref -eq 2
then
    black "Refinement Check: OK"
    red "Synthesis of the control strategies"

    blackn "COMPOSITIONAL MODEL DEMO >> logics_tool -i specs.ltl -o $WD -c synthesis.chase"
    read ans
    logics_tool -i specs.ltl -o $WD -c synthesis.chase

    python3 $SLUGSCOMPILER \
        $WD/joint1.structuredSlugs > $WD/joint1.slugsin
            python3 $SLUGSCOMPILER \
                $WD/joint2.structuredSlugs > $WD/joint2.slugsin
                            python3 $SLUGSCOMPILER \
                                $WD/joint3.structuredSlugs > $WD/joint3.slugsin

                            slugs --explicitStrategy --jsonOutput $WD/joint1.slugsin > $WD/joint1.json
                            slugs --explicitStrategy --jsonOutput $WD/joint2.slugsin > $WD/joint2.json
                            slugs --explicitStrategy --jsonOutput $WD/joint3.slugsin > $WD/joint3.json

                            echo
                            black "FSMs generated: press enter to view the FSMs" ans
                            less $WD/joint1.json
fi


