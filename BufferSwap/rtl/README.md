The files of this directory are from BaseJump STL
(https://github.com/bespoke-silicon-group/basejump_stl, commit c971031248),
unchanged, under the Solderpad Hardware License 0.51 (LICENSE):

- `bsg_dataflow/bsg_two_fifo.sv`, `bsg_dataflow/bsg_one_fifo.sv`
- `bsg_mem/bsg_mem_1r1w.sv`, `bsg_mem/bsg_mem_1r1w_synth.sv`
- `bsg_misc/bsg_dff_reset.sv`, `bsg_misc/bsg_dff_en.sv`, `bsg_misc/bsg_defines.sv`

They are read with the macros `BSG_HIDE_FROM_SYNTHESIS` (no simulation
checks) and `XCELIUM` (the parameters without a value get -1, which Yosys
reads; the default branch leaves them without a value).
