# Checks the contract of the place of the buffer (out/slot.sv, written by
# bufferswap.py) on the RTL of bsg_one_fifo with Jasper. From the directory
# BufferSwap:
#   jg -fpv -batch -tcl jasper/run.tcl
clear -all
set rc [catch {
  analyze -sv12 +define+BSG_HIDE_FROM_SYNTHESIS +define+XCELIUM +incdir+rtl \
    rtl/bsg_defines.sv rtl/bsg_dff_reset.sv rtl/bsg_dff_en.sv rtl/bsg_one_fifo.sv \
    out/slot.sv
  elaborate -top bsg_one_fifo -parameter width_p 4 -disable_auto_bbox
  clock clk_i
  reset -expression {reset_i}
  prove -all -time_limit 300s
  foreach p [get_property_list -include {type assert}] {
    puts "RESULT $p [get_property_info $p -list status]"
  }
} err]
if {$rc} { puts "ERROR $err" }
exit 0
