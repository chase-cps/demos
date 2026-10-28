// The contract of bsg_one_fifo, a buffer of one entry.
module one_fifo (input logic clk, input logic v_i, input logic [3:0] data_i,
                 input logic yumi_i, output logic ready_o, output logic v_o,
                 output logic [3:0] data_o);
  // what the buffer needs from the consumer
  A1: assume property (@(posedge clk) yumi_i |-> v_o);
  A2: assume property (@(posedge clk) v_o |-> s_eventually yumi_i);
  // what it offers stays until it is taken
  G1: assert property (@(posedge clk) v_o && !yumi_i |=> v_o);
  G2: assert property (@(posedge clk) v_o && !yumi_i |=> data_o == $past(data_o));
  // it takes data when it is empty, and after an entry is taken
  G3: assert property (@(posedge clk) !v_o |-> ready_o);
  G4: assert property (@(posedge clk) v_o && yumi_i |=> ready_o);
  // what it takes is offered at the next cycle
  G5: assert property (@(posedge clk) v_i && ready_o |=> v_o);
  // one entry: with a value in, it takes nothing
  G6: assert property (@(posedge clk) v_o |-> !ready_o);
endmodule
