// The sender of the escalation link (simplified from prim_esc_sender of
// OpenTitan). It drives the differential pair esc_p/esc_n: high while an
// escalation is requested, or for one cycle to ping the receiver. It checks
// the response pair resp_p/resp_n: a ping is answered when the response is
// high two cycles after the pulse; equal values on the pair are an
// integrity error.
module esc_sender (
  input  clk,
  input  esc_req,              // escalate
  input  ping_req,             // ping the receiver; held until ping_ok
  input  resp_p_tx, resp_n_tx, // response pair, from the receiver
  output reg esc_p_tx = 1'b0,  // escalation pair, to the receiver
  output reg esc_n_tx = 1'b1,
  output reg ping_ok = 1'b0,   // the ping was answered
  output reg integ_fail = 1'b0 // a wire of the response pair is wrong
);
  reg sent = 1'b0;             // the pulse of the current ping was sent
  reg wait1 = 1'b0, wait2 = 1'b0;
  wire start = ping_req && !esc_req && !sent;
  always @(posedge clk) begin
    esc_p_tx   <= esc_req || start;
    esc_n_tx   <= !(esc_req || start);
    sent       <= ping_req && (sent || start);
    wait1      <= start;
    wait2      <= wait1;
    ping_ok    <= wait2 && resp_p_tx && !resp_n_tx;
    integ_fail <= resp_p_tx == resp_n_tx;
  end
endmodule
