// The whole link: the sender, the wires, and the receiver.
module esc_link_fast (
  input  clk, esc_req, ping_req, err_ep, err_en, err_rp, err_rn,
  output ping_ok, integ_fail, esc_req_o
);
  wire esc_p_tx, esc_n_tx, esc_p_rx, esc_n_rx, resp_p_tx, resp_n_tx, resp_p_rx, resp_n_rx;
  esc_sender_fast s (.clk(clk), .esc_req(esc_req), .ping_req(ping_req),
                  .resp_p_tx(resp_p_tx), .resp_n_tx(resp_n_tx),
                  .esc_p_tx(esc_p_tx), .esc_n_tx(esc_n_tx),
                  .ping_ok(ping_ok), .integ_fail(integ_fail));
  esc_channel  c (.esc_p_tx(esc_p_tx), .esc_n_tx(esc_n_tx),
                  .resp_p_rx(resp_p_rx), .resp_n_rx(resp_n_rx),
                  .err_ep(err_ep), .err_en(err_en), .err_rp(err_rp), .err_rn(err_rn),
                  .esc_p_rx(esc_p_rx), .esc_n_rx(esc_n_rx),
                  .resp_p_tx(resp_p_tx), .resp_n_tx(resp_n_tx));
  esc_receiver r (.clk(clk), .esc_p_rx(esc_p_rx), .esc_n_rx(esc_n_rx),
                  .resp_p_rx(resp_p_rx), .resp_n_rx(resp_n_rx), .esc_req_o(esc_req_o));
endmodule
