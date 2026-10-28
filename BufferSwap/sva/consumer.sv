// The consumer takes data (yumi_i) only when the buffer offers some (v_o),
// and takes what is offered sooner or later.
module consumer (input logic clk, input logic v_o, input logic [3:0] data_o,
                 output logic yumi_i);
  C1: assert property (@(posedge clk) yumi_i |-> v_o);
  C2: assert property (@(posedge clk) v_o |-> s_eventually yumi_i);
endmodule
