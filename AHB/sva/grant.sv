// The arbitration viewpoint: the bus is given to one master, master 1 at the
// start, and no master waits forever.
module grant (input logic clk, input logic hbusreq1, input logic hbusreq2,
              output logic hgrant1, output logic hgrant2);
  initial GR1: assert property (@(posedge clk) hgrant1);
  GR2: assert property (@(posedge clk) hgrant1 != hgrant2);
  // infinitely often master 1 does not ask, or it has the bus
  GR3_1: assert property (@(posedge clk) s_eventually (!hbusreq1 || hgrant1));
  GR3_2: assert property (@(posedge clk) s_eventually (!hbusreq2 || hgrant2));
endmodule
