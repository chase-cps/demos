// The producer offers data with v_i, and keeps offering it until the
// buffer takes it (ready_o).
module producer (input logic clk, input logic ready_o,
                 output logic v_i, output logic [3:0] data_i);
  P1: assert property (@(posedge clk) v_i && !ready_o |=> v_i);
endmodule
