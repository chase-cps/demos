// Contract Arbiter, written by CHASE (chase_cps.to_sva).
// Assumptions: assume property; guarantees: assert property.
module Arbiter_sva (
  input logic clk,
  (* chase = "input" *) input logic hbusreq1,
  (* chase = "input" *) input logic hbusreq2,
  (* chase = "input" *) input logic hlock1,
  (* chase = "input" *) input logic hlock2,
  (* chase = "output" *) input logic hgrant1,
  (* chase = "output" *) input logic hgrant2,
  (* chase = "output" *) input logic hmastlock
);
  // assumptions
  A0: assume property (@(posedge clk)
    hlock1 |-> (hbusreq1));
  A1: assume property (@(posedge clk)
    hlock2 |-> (hbusreq2));
  A2: assume property (@(posedge clk)
    s_eventually (!((hmastlock && ((hgrant1 && hbusreq1) || (hgrant2 && hbusreq2))))));
  // guarantees
  initial G0: assert property (@(posedge clk)
    hgrant1);
  G1: assert property (@(posedge clk)
    !((hgrant1 == hgrant2)));
  G2: assert property (@(posedge clk)
    s_eventually (hbusreq1 |-> (hgrant1)));
  G3: assert property (@(posedge clk)
    s_eventually (hbusreq2 |-> (hgrant2)));
  G4: assert property (@(posedge clk)
    (hmastlock == ((hgrant1 && hlock1) || (hgrant2 && hlock2))));
  G5: assert property (@(posedge clk)
    (hmastlock && hgrant1) |=> (hbusreq1 |-> (hgrant1)));
  G6: assert property (@(posedge clk)
    (hmastlock && hgrant2) |=> (hbusreq2 |-> (hgrant2)));
endmodule
