#!/bin/sh
# Mission refines Target, Target does not refine Mission; Mission || Coordinator is verified.
cd "$(dirname "$0")" && mkdir -p out
chase-cps view specs/robotic_arm.ltl --contracts Mission+Coordinator Target \
    --refines Mission Target --refines Target Mission --check --verify -o out/robotic_arm.html
