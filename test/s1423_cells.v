
module dfnt1v0x2 (cp,d,z);
input cp,d;
output z;
reg z;
always @ (posedge cp)
  z <= d;
endmodule

module an2v0x05 (a,b,z);
input a,b;
output z;
assign z = a*b;
endmodule

module an3v0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = a*b*c;
endmodule

module an4v0x05 (a,b,c,d,z);
input a,b,c,d;
output z;
assign z = a*b*c*d;
endmodule

module aoi112v0x05 (a,b,c1,c2,z);
input a,b,c1,c2;
output z;
assign z = !((c1*c2)+a+b);
endmodule

module aoi21a2v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !((a1*!a2)+b);
endmodule

module aoi21bv0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !((a1*a2)+!b);
endmodule

module aoi21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !((a1*a2)+b);
endmodule

module aoi31v0x05 (a1,a2,a3,b,z);
input a1,a2,a3,b;
output z;
assign z = !((a1*a2*a3)+b);
endmodule

module aon21bv0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = (a1*a2)+!b;
endmodule

module aon21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = (a1*a2)+b;
endmodule

module iv1v0x05 (a,z);
input a;
output z;
assign z = !a;
endmodule

module mxi2v0x05 (a0,a1,s,z);
input a0,a1,s;
output z;
assign z = !((a0*!s)+(a1*s));
endmodule

module mxn2v0x05 (a0,a1,s,z);
input a0,a1,s;
output z;
assign z = (a0*!s)+(a1*s);
endmodule

module nd2av0x05 (a,b,z);
input a,b;
output z;
assign z = a+!b;
endmodule

module nd2v0x05 (a,b,z);
input a,b;
output z;
assign z = !(a*b);
endmodule

module nd3abv0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = !(!a*!b*c);
endmodule

module nd3v0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = !(a*b*c);
endmodule

module nd4v0x05 (a,b,c,d,z);
input a,b,c,d;
output z;
assign z = !(a*b*c*d);
endmodule

module nr2av0x1 (a,b,z);
input a,b;
output z;
assign z = a*!b;
endmodule

module nr2v0x05 (a,b,z);
input a,b;
output z;
assign z = !(a+b);
endmodule

module nr3abv0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = !(!a+!b+c);
endmodule

module nr3av0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = !(!a+b+c);
endmodule

module nr3v0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = !(a+b+c);
endmodule

module nr4v1x05 (a,b,c,d,z);
input a,b,c,d;
output z;
assign z = !(a+b+c+d);
endmodule

module oai211v0x05 (a1,a2,b,c,z);
input a1,a2,b,c;
output z;
assign z = !((a1+a2)*b*c);
endmodule

module oai21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !((a1+a2)*b);
endmodule

module oai22v0x05 (a1,a2,b1,b2,z);
input a1,a2,b1,b2;
output z;
assign z = !((a1+a2)*(b1+b2));
endmodule

module oai31v0x05 (a1,a2,a3,b,z);
input a1,a2,a3,b;
output z;
assign z = !((a1+a2+a3)*b);
endmodule

module oan21bv0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = (a1+a2)*!b;
endmodule

module oan21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = (a1+a2)*b;
endmodule

module or2v0x05 (a,b,z);
input a,b;
output z;
assign z = a+b;
endmodule

module or3v0x05 (a,b,c,z);
input a,b,c;
output z;
assign z = a+b+c;
endmodule

module or4v0x05 (a,b,c,d,z);
input a,b,c,d;
output z;
assign z = a+b+c+d;
endmodule

module xaoi21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !((a1*a2)^b);
endmodule

module xaon21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = (a1*a2)^b;
endmodule

module xnai21v2x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !(!(a1^a2)*b);
endmodule

module xnr2v0x05 (a,b,z);
input a,b;
output z;
assign z = !(a^b);
endmodule

module xooi21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = !((a1+a2)^b);
endmodule

module xoon21v0x05 (a1,a2,b,z);
input a1,a2,b;
output z;
assign z = (a1+a2)^b;
endmodule

module xor2v0x05 (a,b,z);
input a,b;
output z;
assign z = a^b;
endmodule
