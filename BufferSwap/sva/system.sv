// The requirements of the whole system (producer, buffer, consumer): every
// offer is taken sooner or later, and what the buffer offers stays until it
// is taken.
module system (input logic clk, output logic v_i, output logic [3:0] data_i,
               output logic yumi_i, output logic ready_o, output logic v_o,
               output logic [3:0] data_o);
  S1: assert property (@(posedge clk) v_i |-> s_eventually (v_i && ready_o));
  S2: assert property (@(posedge clk) v_o && !yumi_i |=> v_o);
  S3: assert property (@(posedge clk) v_o && !yumi_i |=> data_o == $past(data_o));
endmodule
