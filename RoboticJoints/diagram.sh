#!/bin/sh
# Joint1 || Joint2 || Joint3 refines Joints, and each contract is realizable.
cd "$(dirname "$0")" && mkdir -p out
chase-cps view specs.ltl --contracts Joints \
    --refines Joint1+Joint2+Joint3 Joints --check --realizable -o out/specs.html
