// Simple testbench
module simple_tb;

reg clk;
reg rst;
wire [7:0] count;

simple #(.WIDTH(8)) dut (
    .clk(clk),
    .rst(rst),
    .count(count)
);

initial begin
    clk = 0;
    forever #5 clk = ~clk;
end

initial begin
    rst = 1;
    #20 rst = 0;
    #100;
    if (count > 0) begin
        $display("PASS: Counter reached %0d", count);
    end else begin
        $display("FAIL: Counter did not increment");
        $finish(1);
    end
    $finish(0);
end

endmodule
