// Contract of the receiver.
module receiver (input logic clk, input logic esc_p_rx, input logic esc_n_rx,
                 output logic resp_p_rx, output logic resp_n_rx, output logic esc_req_o);
  // no escalation at the start
  initial R1: assert property (@(posedge clk) !esc_req_o ##1 !esc_req_o);
  // two cycles high on the escalation pair escalate
  R2: assert property (@(posedge clk)
    esc_p_rx && !esc_n_rx ##1 esc_p_rx && !esc_n_rx |=> esc_req_o);
  // and only that
  R3: assert property (@(posedge clk) !esc_p_rx |=> ##1 !esc_req_o);
  R4: assert property (@(posedge clk) !esc_p_rx |=> !esc_req_o);
  // equal values on the escalation pair are signalled back
  R5: assert property (@(posedge clk) esc_p_rx == esc_n_rx |=> resp_p_rx && resp_n_rx);
  // a differential escalation pair gives a differential response pair
  R6: assert property (@(posedge clk) esc_p_rx != esc_n_rx |=> resp_p_rx != resp_n_rx);
  // a rising edge is answered
  R7: assert property (@(posedge clk)
    !esc_p_rx ##1 esc_p_rx && !esc_n_rx |=> resp_p_rx && !resp_n_rx);
endmodule
