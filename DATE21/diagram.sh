#!/bin/sh
# Mission refines Target, Target does not refine Mission (Mission and Target
# drawn open), and System = Mission || Coordinator || Move || Turn || Pick || Place,
# with the checks of each part: compatible (A), consistent (G), realizable (R).
cd "$(dirname "$0")" && mkdir -p out
chase-cps view specs/robotic_arm.ltl \
    --contracts Target Mission Mission+Coordinator+Move+Turn+Pick+Place \
    --refines Mission Target --refines Target Mission --check --verify --realizable \
    --open Mission Target -o out/robotic_arm.html
