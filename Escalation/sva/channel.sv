// Contract of the wires: each err_* input flips one wire.
module channel (input logic clk, input logic esc_p_tx, input logic esc_n_tx,
                input logic resp_p_rx, input logic resp_n_rx,
                input logic err_ep, input logic err_en, input logic err_rp, input logic err_rn,
                output logic esc_p_rx, output logic esc_n_rx,
                output logic resp_p_tx, output logic resp_n_tx);
  C1: assert property (@(posedge clk) esc_p_rx == (esc_p_tx != err_ep));
  C2: assert property (@(posedge clk) esc_n_rx == (esc_n_tx != err_en));
  C3: assert property (@(posedge clk) resp_p_tx == (resp_p_rx != err_rp));
  C4: assert property (@(posedge clk) resp_n_tx == (resp_n_rx != err_rn));
endmodule
