// A single wrong wire is detected by the sender.
module integrity (input logic clk,
                  input logic err_ep, input logic err_en, input logic err_rp, input logic err_rn,
                  output logic integ_fail);
  // one wire of the escalation pair
  I1: assert property (@(posedge clk) err_ep != err_en ##1 !err_rp && !err_rn |=> integ_fail);
  // one wire of the response pair
  I2: assert property (@(posedge clk) !err_ep && !err_en ##1 err_rp != err_rn |=> integ_fail);
endmodule
