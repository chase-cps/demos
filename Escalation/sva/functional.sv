// What the link must do when no wire is wrong.
module functional (input logic clk, input logic esc_req, input logic ping_req,
                   input logic err_ep, input logic err_en, input logic err_rp, input logic err_rn,
                   output logic esc_req_o, output logic ping_ok);
  A1: assume property (@(posedge clk) !err_ep && !err_en && !err_rp && !err_rn);
  // an escalation request held for two cycles escalates the receiver
  F1: assert property (@(posedge clk) esc_req ##1 esc_req |=> ##1 esc_req_o);
  // the receiver does not escalate without a request
  F2: assert property (@(posedge clk) !esc_req ##1 !esc_req |=> ##1 !esc_req_o);
  // a new ping request is answered
  F3: assert property (@(posedge clk)
    !ping_req && !esc_req ##1 ping_req && !esc_req |=> ##2 ping_ok);
endmodule
