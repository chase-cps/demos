// Contract Slot, written by CHASE (chase_cps.to_sva).
// Assumptions: assume property; guarantees: assert property.
module Slot_sva (
  input logic clk_i,
  input logic reset_i,
  (* chase = "input" *) input logic v_i,
  (* chase = "input" *) input logic yumi_i,
  (* chase = "output" *) input logic ready_o,
  (* chase = "output" *) input logic v_o,
  (* chase = "output" *) input logic [3:0] data_o
);
  // assumptions
  A0: assume property (@(posedge clk_i) disable iff (reset_i)
    (v_i && !(ready_o)) |=> (v_i));
  A1: assume property (@(posedge clk_i) disable iff (reset_i)
    yumi_i |-> (v_o));
  A2: assume property (@(posedge clk_i) disable iff (reset_i)
    v_o |-> (s_eventually (yumi_i)));
  // guarantees
  G0: assert property (@(posedge clk_i) disable iff (reset_i)
    v_i |-> (s_eventually ((v_i && ready_o))));
  G1: assert property (@(posedge clk_i) disable iff (reset_i)
    (v_o && !(yumi_i)) |=> (v_o));
  G2: assert property (@(posedge clk_i) disable iff (reset_i)
    (v_o && !(yumi_i)) |=> ((data_o == $past(data_o))));
endmodule

bind bsg_one_fifo Slot_sva Slot_sva_i (.*, .ready_o(ready_and_o));
