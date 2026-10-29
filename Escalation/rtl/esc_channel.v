// The wires between the sender and the receiver. Each err_* input flips
// one wire: a fault, or an attack on the link.
module esc_channel (
  input  esc_p_tx, esc_n_tx, resp_p_rx, resp_n_rx,
  input  err_ep, err_en, err_rp, err_rn,
  output esc_p_rx, esc_n_rx, resp_p_tx, resp_n_tx
);
  assign esc_p_rx  = esc_p_tx  ^ err_ep;
  assign esc_n_rx  = esc_n_tx  ^ err_en;
  assign resp_p_tx = resp_p_rx ^ err_rp;
  assign resp_n_tx = resp_n_rx ^ err_rn;
endmodule
