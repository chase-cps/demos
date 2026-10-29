#!/bin/sh
# Joint1 || Joint2 || Joint3 refines Joints, and each contract is realizable.
# Joint1 and Joints are drawn open: what one joint and the arm guarantee.
cd "$(dirname "$0")" && mkdir -p out
chase-cps view specs.ltl --contracts Joints \
    --refines Joint1+Joint2+Joint3 Joints --check --realizable \
    --open Joint1 Joints -o out/specs.html
