module counter_testbench () ; 
wire [3:0] out; 
reg clk; 
reg rst_n; 

Counter u0 (
    .out (out[3:0]), 
    .rst_n (rst_n), 
    .clk (clk)
    );

initial begin 
    clk = 1'b0;
    forever #10 clk = ~clk;
end

initial begin 
    rst_n = 1'b0; 
    #4 rst_n = 1'b1;
    #4 rst_n = 1'b0;
end

//initial begin
//    $dumpfile("counter.vad");
//    $dumpvars(0,u0);
//end
//`ifdef  DUMP_FSDB
    initial begin
    	$fsdbDumpfile("./test.fsdb");
    	$fsdbDumpvars();
end
//`endif

initial #500 $finish;
endmodule

