// The receiver of the escalation link (simplified from prim_esc_receiver
// of OpenTitan). Two cycles high on the escalation pair escalate; a rising
// edge is answered on the response pair; equal values on the escalation
// pair are signalled back by equal values on the response pair.
module esc_receiver (
  input  clk,
  input  esc_p_rx, esc_n_rx,    // escalation pair, from the sender
  output reg resp_p_rx = 1'b0,  // response pair, to the sender
  output reg resp_n_rx = 1'b1,
  output reg esc_req_o = 1'b0   // escalate the local block
);
  reg on_q = 1'b0;
  wire on = esc_p_rx && !esc_n_rx;
  always @(posedge clk) begin
    on_q      <= on;
    esc_req_o <= on && on_q;
    if (esc_p_rx == esc_n_rx) begin
      resp_p_rx <= 1'b1; resp_n_rx <= 1'b1;
    end else if (on && !on_q) begin
      resp_p_rx <= 1'b1; resp_n_rx <= 1'b0;
    end else begin
      resp_p_rx <= 1'b0; resp_n_rx <= 1'b1;
    end
  end
endmodule
