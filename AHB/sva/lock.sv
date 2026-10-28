// The locking viewpoint: a master that has locked the bus keeps it while it
// asks for it.
module lock (input logic clk, input logic hbusreq1, input logic hbusreq2,
             input logic hlock1, input logic hlock2,
             output logic hgrant1, output logic hgrant2, output logic hmastlock);
  // a master asks for the bus when it asks for a locked access
  LA1_1: assume property (@(posedge clk) hlock1 |-> hbusreq1);
  LA1_2: assume property (@(posedge clk) hlock2 |-> hbusreq2);
  // a master that has locked the bus stops asking for it sooner or later
  LA2: assume property (@(posedge clk)
    s_eventually !(hmastlock && ((hgrant1 && hbusreq1) || (hgrant2 && hbusreq2))));
  // the bus is locked when its master asks for a locked access
  LK1: assert property (@(posedge clk)
    hmastlock == ((hgrant1 && hlock1) || (hgrant2 && hlock2)));
  // while a master has locked the bus and asks for it, it keeps the bus
  LK2_1: assert property (@(posedge clk) hmastlock && hgrant1 |=> !hbusreq1 || hgrant1);
  LK2_2: assert property (@(posedge clk) hmastlock && hgrant2 |=> !hbusreq2 || hgrant2);
endmodule
