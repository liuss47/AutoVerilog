import argparse
import os


def CreatProject(prjname):

    os.system(f'mkdir -p ./{prjname}/src ./{prjname}/script ./{prjname}/sim ./{prjname}/syn/mapped \
    ./{prjname}/syn/report ./{prjname}/syn/script ./{prjname}/syn/unmapped \
    ./{prjname}/work ./{prjname}/syn/log')


    with open(f"{prjname}/Makefile", "w") as f:
        mk = create_makefile(prjname)
        f.write(mk)

    with open(f"{prjname}/sim/main.cpp", "w") as f:
        cpp = create_simcpp(prjname)
        f.write(cpp)

    with open(f"{prjname}/syn/script/SynFlow.tcl", "w") as f:
        synflow = create_SynFlow(prjname)
        f.write(synflow)

    with open(f"{prjname}/syn/script/Sdc.tcl", "w") as f:
        sdc = create_Sdc(prjname)
        f.write(sdc)



def create_makefile(design):
    text = f"""
# 找到所有 Verilog 文件并生成列表
$(shell find $(abspath ./src) $(abspath ./sim) -name "*.v" > ./sim/filelist_sim.f)
$(shell find $(abspath ./src) -name "*.v" > ./syn/filelist_syn.f)

CSRCS = $(shell find $(abspath ./sim) -name "*.c" -or -name "*.cc" -or -name "*.cpp")
VSRC = $(shell cat ./sim/filelist_sim.f)
path = $(OBJ_DIR)/testprj.vcd

CPPFLAGS =
ifeq ($(trace), 1)
CPPFLAGS += -DTRACE_ON
endif

TOPNAME = {design}
BUILD_DIR = ./build
OBJ_DIR = $(BUILD_DIR)/obj_dir
BIN = $(BUILD_DIR)/V$(TOPNAME)
SIMTOP = $(BUILD_DIR)/simtop
LOG_PATH = $(BUILD_DIR)/log
TIMESCALE := 1ns/1ps

# 创建目录
$(shell mkdir -p $(BUILD_DIR))
$(shell mkdir -p $(LOG_PATH))

# 编译目标
compile: clean comp

# 为所有 Verilog 文件添加包含目录
VCS := vcs +v2k -full64 -debug_acc+all -debug_region+cell+encrypt \\
        -LDFLAGS -Wl,--no-as-needed -timescale=${{TIMESCALE}} \\
        -o $(SIMTOP) -l ${{LOG_PATH}}/report.log \\
        -P $(VERDI_HOME)/share/PLI/VCS/LINUXAMD64/novas.tab \\
        $(VERDI_HOME)/share/PLI/VCS/LINUXAMD64/pli.a \\
        +incdir+$(abspath ./src) +incdir+$(abspath ./sim)

comp: $(VSRC)
\t${{VCS}} $^
\t./${{SIMTOP}} -l ${{LOG_PATH}}/run.log
\t@if [ -f novas_dump.log ]; then mv novas_dump.log $(BUILD_DIR)/novas_dump.log; fi;
\t@if [ -d csrc ]; then rm -rf $(BUILD_DIR)/csrc; cp -r csrc $(BUILD_DIR)/csrc; fi;
\t@if [ -f ucli.key ]; then mv ucli.key $(BUILD_DIR)/ucli.key; fi;
\t@if [ -f test.fsdb ]; then mv test.fsdb ./$(BUILD_DIR)/test.fsdb; fi;


all: $(VSRC)
\tverilator -cc -exe --build +define+USE_RF_DEBUG+SNPS_FAST_SIM_FFV main.cpp $^ -top-module top --trace -CFLAGS "$(CPPFLAGS)" -Wno-WIDTH -Wno-CMPCONST -Wno-REDEFMACRO --timescale-override 1ns/1ps
\t-$(BUILD_DIR)/Vtop

sim: $(VSRC) $(CSRCS)
\trm -rf $(OBJ_DIR)
\tverilator -cc -exe --build -Wall $^ -top-module top --trace -CFLAGS "$(CPPFLAGS) -DSIM_ON " -Wno-WIDTH -Wno-CMPCONST -Wno-REDEFMACRO --Mdir $(OBJ_DIR) --timescale-override 1ns/1ps -o $(abspath $(BIN))
\t-$(BUILD_DIR)/Vtop

v2f:
\t@if [ -f $(path) ]; then cd $(OBJ_DIR); vcd2fsdb ./testprj.vcd; fi;

verdi: $(VSRC)
\tcd sim && \\
\tverdi -f filelist_sim.f -ssf ../$(BUILD_DIR)/test.fsdb &

syn:
\t@cd work && dc_shell -f ../syn/script/SynFlow.tcl -output_log_file ../syn/log/top_syn.log

clean:
\trm -rf ./sim/verdiLog ./sim/novas.* ./sim/vcd2fsdbLog $(BUILD_DIR)/csrc $(BUILD_DIR)/novas_dump.log $(BUILD_DIR)/ucli.key

default: all

.PHONY: clean v2f all run syn verdi sim compile
    """
    return text






def create_simcpp(design):
    text = f"""
  #include "Vtop.h"
  #include "verilated.h"
  #include "verilated_vcd_c.h"
  #include <stdio.h>
  #include <stdlib.h>
  #include <assert.h>


  int main(int argc, char** argv, char** env) {{
      #ifdef SIM_ON
      VerilatedContext* contextp = new VerilatedContext;
      contextp->commandArgs(argc, argv);
      Vtop* top = new Vtop{{contextp}};
      int cycle_num=66;
      uint64_t limit = cycle_num;
      #endif
      
      #ifdef TRACE_ON
        printf("=======TRACE_ON=======\\n");
        VerilatedVcdC* tfp = new VerilatedVcdC;
        Verilated::traceEverOn(true);
        top->trace(tfp, 99);
        tfp->open("build/obj_dir/{design}.vcd");
        unsigned int cycle = 0;
      #endif
      //printf("cycle_num = %d \\n",cycle_num);
    
      #ifdef SIM_ON
      while(contextp->time() < limit && !contextp->gotFinish()){{


        int a = rand() & 1;
        int b = rand() & 1;
        top->a = a;
        top->b = b;
        contextp->timeInc(1);
        top->eval();
        //assert((top->f )== (a ^ b));
        //printf("a = %d, b = %d, f = %d\\n", a, b, top->f);


        #ifdef TRACE_ON
            tfp->dump(cycle++);
        #endif
        
      }}
      #endif
      #ifdef TRACE_ON
        tfp->close();
      #endif
      #ifdef SIM_ON
      delete top;
      delete contextp;
      #endif
      return 0;
  }}

    """
    return text


def create_SynFlow(design):
    text = f"""
#--------------------------Specify Libraries--------------------------
set DESIGN_PATH  /home/summer/Synopsys/syn/FreePDK/FreePDK45/osu_soc/lib/files
set search_path "$search_path $DESIGN_PATH"
set target_library "gscl45nm.db"
set link_library "* $target_library"
echo "\\n\\nSettings:"
echo "search_path: $search_path"
echo "link_library: $link_library"
echo "target_library: $target_library"
echo "\\n\\nI'm Ready!"
#set search_path "$TAR_PATH $MEM_LINK_PATH"

#--------------------------Prepare Filelist---------------------------
set FILE_LIST ""
set f [open "../syn/filelist_syn.f" r]
while {{![eof $f]}} {{
    gets $f line
    append FILE_LIST "$line "
}}
echo $FILE_LIST
close $f

#--------------------------Read Designs------------------------------
set TOP_DESIGN {design}
analyze -format verilog $FILE_LIST 
elaborate $TOP_DESIGN

#------------------------Set Current Design&&Link Designs--------------------------
#current_design $TOP_DESIGN(auto)
#link(auto)

#-------------------------------SDC----------------------------------
source ../syn/script/Sdc.tcl

#--------------------Map and Optimize the Design---------------------
compile_ultra -no_autoungroup -incremental -no_boundary_optimization
#----------------------Save Design Database--------------------------
change_names -rules verilog -hierarchy
set_fix_multiple_port_nets -all -buffer_constants
#---------------Check the Synthesized Design for Consistency---------
check_design -summary > ../syn/report/check_design.rpt
check_timing > ../syn/report/check_timing.rpt
#---------------------Report Timing and Area-------------------------
report_qor                  > ../syn/report/$TOP_DESIGN.qor_rpt
report_timing -max_paths 1000 > ../syn/report/$TOP_DESIGN.timing_rpt
report_timing -path full    > ../syn/report/$TOP_DESIGN.full_timing_rpt
report_timing -delay max    > ../syn/report/$TOP_DESIGN.setup_timing_rpt
report_timing -delay min    > ../syn/report/$TOP_DESIGN.hold_timing_rpt
report_reference            > ../syn/report/$TOP_DESIGN.ref_rpt
report_area                 > ../syn/report/$TOP_DESIGN.area_rpt
report_constraints          > ../syn/report/$TOP_DESIGN.const_rpt
report_constraint -all_violators > ../syn/report/$TOP_DESIGN.violators_rpt
report_power > ../syn/report/$TOP_DESIGN.power_rpt
check_timing > ../syn/log/last_check_timing.log
#---------------------Generate Files -------------------------
write -f verilog -hierarchy -output ../syn/mapped/$TOP_DESIGN.v
write_sdc ../syn/mapped/$TOP_DESIGN.sdc
write_sdf -context verilog ../syn/mapped/$TOP_DESIGN.sdf


    """
    return text
	

def create_Sdc(design):
    text = f"""
#==================================Env Vars===================================
set RST_NAME				rst_n
set CLK_NAME				clk

set CLK_PERIOD_I			10
set CLK_PERIOD            	[expr $CLK_PERIOD_I*0.95]
set CLK_SKEW              	[expr $CLK_PERIOD*0.05]
set CLK_SOURCE_LATENCY   	[expr $CLK_PERIOD*0.1]    
set CLK_NETWORK_LATENCY   	[expr $CLK_PERIOD*0.1]  
set CLK_TRAN             	[expr $CLK_PERIOD*0.01]

set INPUT_DELAY_MAX         [expr $CLK_PERIOD*0.4]
set INPUT_DELAY_MIN           0
set OUTPUT_DELAY_MAX        [expr $CLK_PERIOD*0.4]
set OUTPUT_DELAY_MIN          0

set MAX_FANOUT             6
set MAX_TRAN               5
set MAX_CAP                1.5

set ALL_INPUT_EX_CLK [remove_from_collection [all_inputs] [get_ports $CLK_NAME]]
#==================================Define Design Environment=========================
#GUIDANCE: use the default
set_max_area 0
#set_max_transition  $MAX_TRAN     [current_design]
#set_max_fanout      $MAX_FANOUT   [current_design]
#set_max_capacitance $MAX_CAP      [current_design]

#============================= Set Design Constraints=========================
#--------------------------------Clock and Reset Definition----------------------------
set_drive 0 [get_ports $CLK_NAME]
create_clock -name $CLK_NAME -period $CLK_PERIOD [get_ports $CLK_NAME]
set_dont_touch_network [get_ports $CLK_NAME]

set_clock_uncertainty $CLK_SKEW [get_clocks $CLK_NAME]
set_clock_transition  $CLK_TRAN [all_clocks]
set_clock_latency -source $CLK_SOURCE_LATENCY [get_clocks $CLK_NAME]
set_clock_latency -max $CLK_NETWORK_LATENCY [get_clocks $CLK_NAME]
#rst_ports
set_drive 0            				[get_ports $RST_NAME]
set_dont_touch_network 				[get_ports $RST_NAME]
set_false_path -from   				[get_ports $RST_NAME] 
set_ideal_network -no_propagate     [get_ports $RST_NAME]


#--------------------------------I/O Constraint-----------------------------
set_input_delay   -max $INPUT_DELAY_MAX   -clock $CLK_NAME   $ALL_INPUT_EX_CLK
set_input_delay   -min $INPUT_DELAY_MIN   -clock $CLK_NAME   $ALL_INPUT_EX_CLK -add
set_output_delay  -max $OUTPUT_DELAY_MAX  -clock $CLK_NAME   [all_outputs]
set_output_delay  -min $OUTPUT_DELAY_MIN  -clock $CLK_NAME   [all_outputs] -add
set_load  0.2 	[all_outputs]	

    """
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build helper')
    parser.add_argument('vprjs', metavar='prjname', type=str, nargs='+',
                        help='input building prj name')

    args = parser.parse_args()
    for vprj in args.vprjs:
        CreatProject(vprj)
