// Contract of the sender.
module sender (input logic clk, input logic esc_req, input logic ping_req,
               input logic resp_p_tx, input logic resp_n_tx,
               output logic esc_p_tx, output logic esc_n_tx,
               output logic ping_ok, output logic integ_fail);
  // the escalation pair starts low, and is always differential
  initial S1: assert property (@(posedge clk) !esc_p_tx);
  S2: assert property (@(posedge clk) esc_n_tx == !esc_p_tx);
  // an escalation request raises the pair at the next cycle
  S3: assert property (@(posedge clk) esc_req |=> esc_p_tx);
  // without a request, the pair stays low
  S4: assert property (@(posedge clk) !esc_req && !ping_req |=> !esc_p_tx);
  // the pair is high two cycles in a row only for an escalation request
  S5: assert property (@(posedge clk) !esc_req ##1 !esc_req && esc_p_tx |=> !esc_p_tx);
  // a new ping request sends a pulse
  S6: assert property (@(posedge clk) !ping_req && !esc_req ##1 ping_req && !esc_req |=> esc_p_tx);
  // the ping is answered when the response comes two cycles after the pulse
  S7: assert property (@(posedge clk)
    !ping_req && !esc_req ##1 ping_req && !esc_req ##2 resp_p_tx && !resp_n_tx |=> ping_ok);
  // equal values on the response pair are an integrity error
  S8: assert property (@(posedge clk) resp_p_tx == resp_n_tx |=> integ_fail);
endmodule
