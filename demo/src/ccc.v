module Counter (out, clk, rst_n); 
input clk, rst_n; 
output [3:0] out; 
reg [3:0] out; 

always @(posedge clk or posedge rst_n) begin
    if (rst_n) begin
        // reset
        out <= 4'b0;
    end
    else begin
        out <= out + 1'b1;
    end
end

endmodule

