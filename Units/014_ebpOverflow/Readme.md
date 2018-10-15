## Instructions and Analysis

### Instructions

> First of all, understand the source code before compile it

```
gcc -o func -fno-stack-protector -g functest.c

```
> Secondary, using the GDB to run the code 

```
gdb -q ./func 

```
> normally, the unexpected "hello world" should appears

### Analysis

> This code aims to modify the $rsp instead of return address

> So disass the main() and func2() respectively

```
gef   disass main
Dump of assembler code for function main:
   0x000000000040069a <+0>:	push   rbp
   0x000000000040069b <+1>:	mov    rbp,rsp
   0x000000000040069e <+4>:	sub    rsp,0x30
   0x00000000004006a2 <+8>:	lea    rax,[rbp-0x30]
   0x00000000004006a6 <+12>:	mov    QWORD PTR [rbp-0x8],rax
   0x00000000004006aa <+16>:	lea    rax,[rbp-0x30]
   0x00000000004006ae <+20>:	mov    edx,0x14
   0x00000000004006b3 <+25>:	mov    esi,0x61
   0x00000000004006b8 <+30>:	mov    rdi,rax
   0x00000000004006bb <+33>:	call   0x400500 <memset@plt>
   0x00000000004006c0 <+38>:	mov    QWORD PTR [rbp-0x10],0x400670
   0x00000000004006c8 <+46>:	mov    rax,QWORD PTR [rbp-0x10]
   0x00000000004006cc <+50>:	mov    rsi,rax
   0x00000000004006cf <+53>:	mov    edi,0x400790
   0x00000000004006d4 <+58>:	mov    eax,0x0
   0x00000000004006d9 <+63>:	call   0x4004f0 <printf@plt>
   0x00000000004006de <+68>:	add    QWORD PTR [rbp-0x8],0x18
   0x00000000004006e3 <+73>:	mov    rax,QWORD PTR [rbp-0x8]
   0x00000000004006e7 <+77>:	mov    rdi,rax
   0x00000000004006ea <+80>:	call   0x40062d <func1>
   0x00000000004006ef <+85>:	mov    edi,0x400798
   0x00000000004006f4 <+90>:	call   0x4004e0 <puts@plt>
   0x00000000004006f9 <+95>:	mov    eax,0x0
   0x00000000004006fe <+100>:	leave 
   0x00000000004006ff <+101>:	ret

```
> the Stack alloc 0x30 for variable a[20],p and s 
>> in the stack it looks as below:
```
gef   x /40x $rsp
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161  | a[20]
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000  | 
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff  | p and s accordingly (2 Byte aligned)
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0xd4cf9c6d	0xc658e4b2
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdce0:	0x6def9c6d	0x39a71b4d	0x89359c6d	0x39a70bf4
```
* from 0x.dc50 to 0x.dc70 is a[20]
* from 0x.dc70 to 0x.dc78 is p(entry addr of func2) That means 0x400670 is the entry addr of func2
* from 0x.dc78 to 0x.dc80 is s( a[0](0x.dc50) + 24 = 0x.dc68) It aims to set the $ebp locate right before the addr of func2
So when the $ebp pop the stack, it will go straight at the func2 instead of backing to main function.

*** how to calculate the x of s += x,  find the expected addr of $ebp(0x7fffffffdc60 right before the entry addr of func2) and the $ebp of main (0x7fffffffdc80 right before the return addr of main)  0x.dc80 - 0x.dc68 = 0x18 = 24

> before the memcpy the stack is as below:
```
gef  x /40x $rsp
0x7fffffffdc20:	0x00400790	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc30:	0x61616161	0x00007fff	0xf7ffe1c8	0x00000004
0x7fffffffdc40:	0xffffdc80	0x00007fff	0x004006ef	0x00000000
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0xd4cf9c6d	0xc658e4b2

```
* according to the previous analysis, the purpose of memcpy is to modify the 0xffffdc80 with 0xffffdc68
* so a[4] is at 0x.dc30  the  $rsp is at 0x.dc44
* then 0x.dc44 - 0x.dc40 = 0x14  so memcpy(a,s,20)

> when breakpoint comes to  0x00000000004006fe <+100>:	leave 
* $ebp  0x.dc68 pop from the stack, return addr is  0x004006ef, now back to the main()
* 0x400540 was reognized as $ebp, return addr is 0x400670, which is exactly the addr of func2
* finally, hello world appears!

### appendix

```
1	
2	#include <stdio.h>
3	#include <string.h>
4	
5	void func1(char *s)
6	{
7	    char a[4];
8	    int j;
9	    for ( j = 0 ; j < 4; j++)
10		   a[j] = 'a'; 
gef  l 
11	    memcpy(a,s,20);
12	}
13	
14	void func2(void)
15	{
16	    printf("hello,world\n");
17	}
18	
19	void func3(char *s)
20	{
gef   l
21	    func1(s);
22	}
23	
24	int main(void)
25	{
26	    void (*p)(void);
27	    char a[20] ;
28	    char *s = a;
29	    memset(a,'a',20);
30	    
gef   l
31	#if 0 
32	    for(i = 0; i < 8; i++)
33		    //a[i] = 0;
34	            a[i] = '\0';
35	    
36	#endif
37	    
38	    p = func2;
39	    printf("p is %p",p);
40	    s = s + 24;
gef  l
41	    func1(s);
42	    printf("really!\n");
43	    return 0;
44	}
45	
gef   disass main
Dump of assembler code for function main:
   0x000000000040069a <+0>:	push   rbp
   0x000000000040069b <+1>:	mov    rbp,rsp
   0x000000000040069e <+4>:	sub    rsp,0x30
   0x00000000004006a2 <+8>:	lea    rax,[rbp-0x30]
   0x00000000004006a6 <+12>:	mov    QWORD PTR [rbp-0x8],rax
   0x00000000004006aa <+16>:	lea    rax,[rbp-0x30]
   0x00000000004006ae <+20>:	mov    edx,0x14
   0x00000000004006b3 <+25>:	mov    esi,0x61
   0x00000000004006b8 <+30>:	mov    rdi,rax
   0x00000000004006bb <+33>:	call   0x400500 <memset@plt>
   0x00000000004006c0 <+38>:	mov    QWORD PTR [rbp-0x10],0x400670
   0x00000000004006c8 <+46>:	mov    rax,QWORD PTR [rbp-0x10]
   0x00000000004006cc <+50>:	mov    rsi,rax
   0x00000000004006cf <+53>:	mov    edi,0x400790
   0x00000000004006d4 <+58>:	mov    eax,0x0
   0x00000000004006d9 <+63>:	call   0x4004f0 <printf@plt>
   0x00000000004006de <+68>:	add    QWORD PTR [rbp-0x8],0x18
   0x00000000004006e3 <+73>:	mov    rax,QWORD PTR [rbp-0x8]
   0x00000000004006e7 <+77>:	mov    rdi,rax
   0x00000000004006ea <+80>:	call   0x40062d <func1>
   0x00000000004006ef <+85>:	mov    edi,0x400798
   0x00000000004006f4 <+90>:	call   0x4004e0 <puts@plt>
   0x00000000004006f9 <+95>:	mov    eax,0x0
   0x00000000004006fe <+100>:	leave  
=> 0x00000000004006ff <+101>:	ret    
End of assembler dump.
gef   disass func1
Dump of assembler code for function func1:
   0x000000000040062d <+0>:	push   rbp
   0x000000000040062e <+1>:	mov    rbp,rsp
   0x0000000000400631 <+4>:	sub    rsp,0x20
   0x0000000000400635 <+8>:	mov    QWORD PTR [rbp-0x18],rdi
   0x0000000000400639 <+12>:	mov    DWORD PTR [rbp-0x4],0x0
   0x0000000000400640 <+19>:	jmp    0x400650 <func1+35>
   0x0000000000400642 <+21>:	mov    eax,DWORD PTR [rbp-0x4]
   0x0000000000400645 <+24>:	cdqe   
   0x0000000000400647 <+26>:	mov    BYTE PTR [rbp+rax*1-0x10],0x61
   0x000000000040064c <+31>:	add    DWORD PTR [rbp-0x4],0x1
   0x0000000000400650 <+35>:	cmp    DWORD PTR [rbp-0x4],0x3
   0x0000000000400654 <+39>:	jle    0x400642 <func1+21>
   0x0000000000400656 <+41>:	mov    rcx,QWORD PTR [rbp-0x18]
   0x000000000040065a <+45>:	lea    rax,[rbp-0x10]
   0x000000000040065e <+49>:	mov    edx,0x14
   0x0000000000400663 <+54>:	mov    rsi,rcx
   0x0000000000400666 <+57>:	mov    rdi,rax
   0x0000000000400669 <+60>:	call   0x400530 <memcpy@plt>
   0x000000000040066e <+65>:	leave  
   0x000000000040066f <+66>:	ret    
End of assembler dump.
gef   disass func2
Dump of assembler code for function func2:
   0x0000000000400670 <+0>:	push   rbp
   0x0000000000400671 <+1>:	mov    rbp,rsp
   0x0000000000400674 <+4>:	mov    edi,0x400784
   0x0000000000400679 <+9>:	call   0x4004e0 <puts@plt>
   0x000000000040067e <+14>:	pop    rbp
   0x000000000040067f <+15>:	ret    
End of assembler dump.
gef  b *0x40069a
Breakpoint 3 at 0x40069a: file functest.c, line 25.
gef  b *0x40069b
Breakpoint 4 at 0x40069b: file functest.c, line 25.
gef  b *0x40069e
Breakpoint 5 at 0x40069e: file functest.c, line 25.
gef  b *0x4006ea
Breakpoint 6 at 0x4006ea: file functest.c, line 41.
gef  b *0x40062d
Breakpoint 7 at 0x40062d: file functest.c, line 6.
gef  b *0x40062e
Breakpoint 8 at 0x40062e: file functest.c, line 6.
gef  b *0x400631
Breakpoint 9 at 0x400631: file functest.c, line 6.
gef  b *0x400669
Breakpoint 10 at 0x400669: file functest.c, line 11.
gef  b *0x40066e
Breakpoint 11 at 0x40066e: file functest.c, line 12.
gef  b *0x40066f
Breakpoint 12 at 0x40066f: file functest.c, line 12.
gef  b *0x4006fe
Note: breakpoint 1 also set at pc 0x4006fe.
Breakpoint 13 at 0x4006fe: file functest.c, line 44.
gef  b *0x4006ff
Note: breakpoint 2 also set at pc 0x4006ff.
Breakpoint 14 at 0x4006ff: file functest.c, line 44.
gef  r
Starting program: /home/zpy/devel/test/functest/func 

Breakpoint 3, main () at functest.c:25
25	{
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x40069a            ¡ú  <main+0> push rbp
$rbx   : 0x0               
$rcx   : 0x0               
$rdx   : 0x7fffffffdd78      ¡ú  0x00007fffffffe135  ¡ú  "LC_PAPER=zh_CN.UTF-8"
$rsp   : 0x7fffffffdc88      ¡ú  0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax
$rbp   : 0x0               
$rsi   : 0x7fffffffdd68      ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
$rdi   : 0x1               
$rip   : 0x40069a            ¡ú  <main+0> push rbp
$r8    : 0x7ffff7dd4e80      ¡ú  0x0000000000000000
$r9    : 0x7ffff7dea600      ¡ú  <_dl_fini+0> push rbp
$r10   : 0x7fffffffdb10      ¡ú  0x0000000000000000
$r11   : 0x7ffff7a32e50      ¡ú  <__libc_start_main+0> push r14
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc88©¦+0x00: 0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax	 ¡û $rsp
0x00007fffffffdc90©¦+0x08: 0x0000000000000000
0x00007fffffffdc98©¦+0x10: 0x00007fffffffdd68  ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
0x00007fffffffdca0©¦+0x18: 0x0000000100000000
0x00007fffffffdca8©¦+0x20: 0x000000000040069a  ¡ú  <main+0> push rbp
0x00007fffffffdcb0©¦+0x28: 0x0000000000000000
0x00007fffffffdcb8©¦+0x30: 0x1a844df63758b263
0x00007fffffffdcc0©¦+0x38: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400693 <func3+19>       call   0x40062d <func1>
     0x400698 <func3+24>       leave  
     0x400699 <func3+25>       ret    
 ¡ú   0x40069a <main+0>         push   rbp
     0x40069b <main+1>         mov    rbp, rsp
     0x40069e <main+4>         sub    rsp, 0x30
     0x4006a2 <main+8>         lea    rax, [rbp-0x30]
     0x4006a6 <main+12>        mov    QWORD PTR [rbp-0x8], rax
     0x4006aa <main+16>        lea    rax, [rbp-0x30]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+25 ]©¤©¤©¤©¤
     20	 {
     21	     func1(s);
     22	 }
     23	 
     24	 int main(void)
 ¡ú   25	 {
     26	     void (*p)(void);
     27	     char a[20] ;
     28	     char *s = a;
     29	     memset(a,'a',20);
     30	 
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40069a ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef   x /40x $rsp
0x7fffffffdc88:	0xf7a32f45	0x00007fff	0x00000000	0x00000000
0x7fffffffdc98:	0xffffdd68	0x00007fff	0x00000000	0x00000001
0x7fffffffdca8:	0x0040069a	0x00000000	0x00000000	0x00000000
0x7fffffffdcb8:	0x3758b263	0x1a844df6	0x00400540	0x00000000
0x7fffffffdcc8:	0xffffdd60	0x00007fff	0x00000000	0x00000000
0x7fffffffdcd8:	0x00000000	0x00000000	0x8e78b263	0xe57bb209
0x7fffffffdce8:	0x6aa2b263	0xe57ba2b0	0x00000000	0x00000000
0x7fffffffdcf8:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdd08:	0x00400700	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdd18:	0x00000001	0x00000000	0x00000000	0x00000000
gef   c
Continuing.

Breakpoint 4, 0x000000000040069b in main () at functest.c:25
25	{
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x40069a            ¡ú  <main+0> push rbp
$rbx   : 0x0               
$rcx   : 0x0               
$rdx   : 0x7fffffffdd78      ¡ú  0x00007fffffffe135  ¡ú  "LC_PAPER=zh_CN.UTF-8"
$rsp   : 0x7fffffffdc80      ¡ú  0x0000000000000000
$rbp   : 0x0               
$rsi   : 0x7fffffffdd68      ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
$rdi   : 0x1               
$rip   : 0x40069b            ¡ú  <main+1> mov rbp, rsp
$r8    : 0x7ffff7dd4e80      ¡ú  0x0000000000000000
$r9    : 0x7ffff7dea600      ¡ú  <_dl_fini+0> push rbp
$r10   : 0x7fffffffdb10      ¡ú  0x0000000000000000
$r11   : 0x7ffff7a32e50      ¡ú  <__libc_start_main+0> push r14
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc80©¦+0x00: 0x0000000000000000	 ¡û $rsp
0x00007fffffffdc88©¦+0x08: 0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax
0x00007fffffffdc90©¦+0x10: 0x0000000000000000
0x00007fffffffdc98©¦+0x18: 0x00007fffffffdd68  ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
0x00007fffffffdca0©¦+0x20: 0x0000000100000000
0x00007fffffffdca8©¦+0x28: 0x000000000040069a  ¡ú  <main+0> push rbp
0x00007fffffffdcb0©¦+0x30: 0x0000000000000000
0x00007fffffffdcb8©¦+0x38: 0x1a844df63758b263
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400697 <func3+23>       dec    ecx
     0x400699 <func3+25>       ret    
     0x40069a <main+0>         push   rbp
 ¡ú   0x40069b <main+1>         mov    rbp, rsp
     0x40069e <main+4>         sub    rsp, 0x30
     0x4006a2 <main+8>         lea    rax, [rbp-0x30]
     0x4006a6 <main+12>        mov    QWORD PTR [rbp-0x8], rax
     0x4006aa <main+16>        lea    rax, [rbp-0x30]
     0x4006ae <main+20>        mov    edx, 0x14
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+25 ]©¤©¤©¤©¤
     20	 {
     21	     func1(s);
     22	 }
     23	 
     24	 int main(void)
 ¡ú   25	 {
     26	     void (*p)(void);
     27	     char a[20] ;
     28	     char *s = a;
     29	     memset(a,'a',20);
     30	 
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40069b ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef  x /40x $rsp
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdce0:	0x8e78b263	0xe57bb209	0x6aa2b263	0xe57ba2b0
0x7fffffffdcf0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdd00:	0x00000000	0x00000000	0x00400700	0x00000000
0x7fffffffdd10:	0xffffdd68	0x00007fff	0x00000001	0x00000000
gef  c
Continuing.

Breakpoint 5, 0x000000000040069e in main () at functest.c:25
25	{
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x40069a            ¡ú  <main+0> push rbp
$rbx   : 0x0               
$rcx   : 0x0               
$rdx   : 0x7fffffffdd78      ¡ú  0x00007fffffffe135  ¡ú  "LC_PAPER=zh_CN.UTF-8"
$rsp   : 0x7fffffffdc80      ¡ú  0x0000000000000000
$rbp   : 0x7fffffffdc80      ¡ú  0x0000000000000000
$rsi   : 0x7fffffffdd68      ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
$rdi   : 0x1               
$rip   : 0x40069e            ¡ú  <main+4> sub rsp, 0x30
$r8    : 0x7ffff7dd4e80      ¡ú  0x0000000000000000
$r9    : 0x7ffff7dea600      ¡ú  <_dl_fini+0> push rbp
$r10   : 0x7fffffffdb10      ¡ú  0x0000000000000000
$r11   : 0x7ffff7a32e50      ¡ú  <__libc_start_main+0> push r14
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc80©¦+0x00: 0x0000000000000000	 ¡û $rsp, $rbp
0x00007fffffffdc88©¦+0x08: 0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax
0x00007fffffffdc90©¦+0x10: 0x0000000000000000
0x00007fffffffdc98©¦+0x18: 0x00007fffffffdd68  ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
0x00007fffffffdca0©¦+0x20: 0x0000000100000000
0x00007fffffffdca8©¦+0x28: 0x000000000040069a  ¡ú  <main+0> push rbp
0x00007fffffffdcb0©¦+0x30: 0x0000000000000000
0x00007fffffffdcb8©¦+0x38: 0x1a844df63758b263
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400699 <func3+25>       ret    
     0x40069a <main+0>         push   rbp
     0x40069b <main+1>         mov    rbp, rsp
 ¡ú   0x40069e <main+4>         sub    rsp, 0x30
     0x4006a2 <main+8>         lea    rax, [rbp-0x30]
     0x4006a6 <main+12>        mov    QWORD PTR [rbp-0x8], rax
     0x4006aa <main+16>        lea    rax, [rbp-0x30]
     0x4006ae <main+20>        mov    edx, 0x14
     0x4006b3 <main+25>        mov    esi, 0x61
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+25 ]©¤©¤©¤©¤
     20	 {
     21	     func1(s);
     22	 }
     23	 
     24	 int main(void)
 ¡ú   25	 {
     26	     void (*p)(void);
     27	     char a[20] ;
     28	     char *s = a;
     29	     memset(a,'a',20);
     30	 
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40069e ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef  x /40x $rsp
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdce0:	0x8e78b263	0xe57bb209	0x6aa2b263	0xe57ba2b0
0x7fffffffdcf0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdd00:	0x00000000	0x00000000	0x00400700	0x00000000
0x7fffffffdd10:	0xffffdd68	0x00007fff	0x00000001	0x00000000
gef c
Continuing.

Breakpoint 6, 0x00000000004006ea in main () at functest.c:41
41	    func1(s);
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rbx   : 0x0               
$rcx   : 0xd               
$rdx   : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$rsp   : 0x7fffffffdc50      ¡ú  "aaaaaaaaaaaaaaaaaaaa"
$rbp   : 0x7fffffffdc80      ¡ú  0x0000000000000000
$rsi   : 0x7ffffff2        
$rdi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rip   : 0x4006ea            ¡ú  <main+80> call 0x40062d <func1>
$r8    : 0x7ffff7b8b640      ¡ú  "0123456789abcdefghijklmnopqrstuvwxyz"
$r9    : 0x0               
$r10   : 0x7ffff7dd26a0      ¡ú  0x0000000000000000
$r11   : 0x0               
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry parity adjust zero sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc50©¦+0x00: "aaaaaaaaaaaaaaaaaaaa"	 ¡û $rsp
0x00007fffffffdc58©¦+0x08: "aaaaaaaaaaaa"
0x00007fffffffdc60©¦+0x10: 0x0000000061616161 ("aaaa"?)
0x00007fffffffdc68©¦+0x18: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rax, $rdi
0x00007fffffffdc70©¦+0x20: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc78©¦+0x28: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc80©¦+0x30: 0x0000000000000000	 ¡û $rbp
0x00007fffffffdc88©¦+0x38: 0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x4006de <main+68>        add    QWORD PTR [rbp-0x8], 0x18
     0x4006e3 <main+73>        mov    rax, QWORD PTR [rbp-0x8]
     0x4006e7 <main+77>        mov    rdi, rax
 ¡ú   0x4006ea <main+80>        call   0x40062d <func1>
   6É9    0x40062d <func1+0>        push   rbp
        0x40062e <func1+1>        mov    rbp, rsp
        0x400631 <func1+4>        sub    rsp, 0x20
        0x400635 <func1+8>        mov    QWORD PTR [rbp-0x18], rdi
        0x400639 <func1+12>       mov    DWORD PTR [rbp-0x4], 0x0
        0x400640 <func1+19>       jmp    0x400650 <func1+35>
[!] Command 'context' failed to execute properly, reason: Type is not a structure, union, or enum type.
gef7Ì2  x /40x $rsp
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdce0:	0x8e78b263	0xe57bb209	0x6aa2b263	0xe57ba2b0
gef7Ì2  c
Continuing.

Breakpoint 7, func1 (s=0x7ffff7dd4e80 <initial> "") at functest.c:6
6	{
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rbx   : 0x0               
$rcx   : 0xd               
$rdx   : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$rsp   : 0x7fffffffdc48      ¡ú  0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798
$rbp   : 0x7fffffffdc80      ¡ú  0x0000000000000000
$rsi   : 0x7ffffff2        
$rdi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rip   : 0x40062d            ¡ú  <func1+0> push rbp
$r8    : 0x7ffff7b8b640      ¡ú  "0123456789abcdefghijklmnopqrstuvwxyz"
$r9    : 0x0               
$r10   : 0x7ffff7dd26a0      ¡ú  0x0000000000000000
$r11   : 0x0               
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry parity adjust zero sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc48©¦+0x00: 0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798	 ¡û $rsp
0x00007fffffffdc50©¦+0x08: "aaaaaaaaaaaaaaaaaaaa"
0x00007fffffffdc58©¦+0x10: "aaaaaaaaaaaa"
0x00007fffffffdc60©¦+0x18: 0x0000000061616161 ("aaaa"?)
0x00007fffffffdc68©¦+0x20: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rax, $rdi
0x00007fffffffdc70©¦+0x28: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc78©¦+0x30: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc80©¦+0x38: 0x0000000000000000	 ¡û $rbp
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400620 <frame_dummy+32> jmp    0x4005a0 <register_tm_clones>
     0x400625 <frame_dummy+37> nop    DWORD PTR [rax]
     0x400628 <frame_dummy+40> jmp    0x4005a0 <register_tm_clones>
 ¡ú   0x40062d <func1+0>        push   rbp
     0x40062e <func1+1>        mov    rbp, rsp
     0x400631 <func1+4>        sub    rsp, 0x20
     0x400635 <func1+8>        mov    QWORD PTR [rbp-0x18], rdi
     0x400639 <func1+12>       mov    DWORD PTR [rbp-0x4], 0x0
     0x400640 <func1+19>       jmp    0x400650 <func1+35>
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+6 ]©¤©¤©¤©¤
      1	 
      2	 #include <stdio.h>
      3	 #include <string.h>
      4	 
      5	 void func1(char *s)
 ¡ú    6	 {
      7	     char a[4];
      8	     int j;
      9	     for ( j = 0 ; j < 4; j++)
     10	 	   a[j] = 'a';
     11	     memcpy(a,s,20);
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40062d ¡ú Name: func1(s=0x7ffff7dd4e80 <initial> "")
[#1] 0x4006ef ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc48:	0x004006ef	0x00000000	0x61616161	0x61616161
0x7fffffffdc58:	0x61616161	0x61616161	0x61616161	0x00000000
0x7fffffffdc68:	0x00400540	0x00000000	0x00400670	0x00000000
0x7fffffffdc78:	0xffffdc68	0x00007fff	0x00000000	0x00000000
0x7fffffffdc88:	0xf7a32f45	0x00007fff	0x00000000	0x00000000
0x7fffffffdc98:	0xffffdd68	0x00007fff	0x00000000	0x00000001
0x7fffffffdca8:	0x0040069a	0x00000000	0x00000000	0x00000000
0x7fffffffdcb8:	0x3758b263	0x1a844df6	0x00400540	0x00000000
0x7fffffffdcc8:	0xffffdd60	0x00007fff	0x00000000	0x00000000
0x7fffffffdcd8:	0x00000000	0x00000000	0x8e78b263	0xe57bb209
gef7Ì2  c
Continuing.

Breakpoint 8, 0x000000000040062e in func1 (s=0x7ffff7dd4e80 <initial> "") at functest.c:6
6	{
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rbx   : 0x0               
$rcx   : 0xd               
$rdx   : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$rsp   : 0x7fffffffdc40      ¡ú  0x00007fffffffdc80  ¡ú  0x0000000000000000
$rbp   : 0x7fffffffdc80      ¡ú  0x0000000000000000
$rsi   : 0x7ffffff2        
$rdi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rip   : 0x40062e            ¡ú  <func1+1> mov rbp, rsp
$r8    : 0x7ffff7b8b640      ¡ú  "0123456789abcdefghijklmnopqrstuvwxyz"
$r9    : 0x0               
$r10   : 0x7ffff7dd26a0      ¡ú  0x0000000000000000
$r11   : 0x0               
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry parity adjust zero sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc40©¦+0x00: 0x00007fffffffdc80  ¡ú  0x0000000000000000	 ¡û $rsp
0x00007fffffffdc48©¦+0x08: 0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798
0x00007fffffffdc50©¦+0x10: "aaaaaaaaaaaaaaaaaaaa"
0x00007fffffffdc58©¦+0x18: "aaaaaaaaaaaa"
0x00007fffffffdc60©¦+0x20: 0x0000000061616161 ("aaaa"?)
0x00007fffffffdc68©¦+0x28: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rax, $rdi
0x00007fffffffdc70©¦+0x30: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc78©¦+0x38: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400625 <frame_dummy+37> nop    DWORD PTR [rax]
     0x400628 <frame_dummy+40> jmp    0x4005a0 <register_tm_clones>
     0x40062d <func1+0>        push   rbp
 ¡ú   0x40062e <func1+1>        mov    rbp, rsp
     0x400631 <func1+4>        sub    rsp, 0x20
     0x400635 <func1+8>        mov    QWORD PTR [rbp-0x18], rdi
     0x400639 <func1+12>       mov    DWORD PTR [rbp-0x4], 0x0
     0x400640 <func1+19>       jmp    0x400650 <func1+35>
     0x400642 <func1+21>       mov    eax, DWORD PTR [rbp-0x4]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+6 ]©¤©¤©¤©¤
      1	 
      2	 #include <stdio.h>
      3	 #include <string.h>
      4	 
      5	 void func1(char *s)
 ¡ú    6	 {
      7	     char a[4];
      8	     int j;
      9	     for ( j = 0 ; j < 4; j++)
     10	 	   a[j] = 'a';
     11	     memcpy(a,s,20);
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40062e ¡ú Name: func1(s=0x7ffff7dd4e80 <initial> "")
[#1] 0x4006ef ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc40:	0xffffdc80	0x00007fff	0x004006ef	0x00000000
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
gef7Ì2  c
Continuing.

Breakpoint 9, 0x0000000000400631 in func1 (s=0x7ffff7dd4e80 <initial> "") at functest.c:6
6	{
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rbx   : 0x0               
$rcx   : 0xd               
$rdx   : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$rsp   : 0x7fffffffdc40      ¡ú  0x00007fffffffdc80  ¡ú  0x0000000000000000
$rbp   : 0x7fffffffdc40      ¡ú  0x00007fffffffdc80  ¡ú  0x0000000000000000
$rsi   : 0x7ffffff2        
$rdi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rip   : 0x400631            ¡ú  <func1+4> sub rsp, 0x20
$r8    : 0x7ffff7b8b640      ¡ú  "0123456789abcdefghijklmnopqrstuvwxyz"
$r9    : 0x0               
$r10   : 0x7ffff7dd26a0      ¡ú  0x0000000000000000
$r11   : 0x0               
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry parity adjust zero sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc40©¦+0x00: 0x00007fffffffdc80  ¡ú  0x0000000000000000	 ¡û $rsp, $rbp
0x00007fffffffdc48©¦+0x08: 0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798
0x00007fffffffdc50©¦+0x10: "aaaaaaaaaaaaaaaaaaaa"
0x00007fffffffdc58©¦+0x18: "aaaaaaaaaaaa"
0x00007fffffffdc60©¦+0x20: 0x0000000061616161 ("aaaa"?)
0x00007fffffffdc68©¦+0x28: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rax, $rdi
0x00007fffffffdc70©¦+0x30: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc78©¦+0x38: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400628 <frame_dummy+40> jmp    0x4005a0 <register_tm_clones>
     0x40062d <func1+0>        push   rbp
     0x40062e <func1+1>        mov    rbp, rsp
 ¡ú   0x400631 <func1+4>        sub    rsp, 0x20
     0x400635 <func1+8>        mov    QWORD PTR [rbp-0x18], rdi
     0x400639 <func1+12>       mov    DWORD PTR [rbp-0x4], 0x0
     0x400640 <func1+19>       jmp    0x400650 <func1+35>
     0x400642 <func1+21>       mov    eax, DWORD PTR [rbp-0x4]
     0x400645 <func1+24>       cdqe   
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+6 ]©¤©¤©¤©¤
      1	 
      2	 #include <stdio.h>
      3	 #include <string.h>
      4	 
      5	 void func1(char *s)
 ¡ú    6	 {
      7	     char a[4];
      8	     int j;
      9	     for ( j = 0 ; j < 4; j++)
     10	 	   a[j] = 'a';
     11	     memcpy(a,s,20);
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x400631 ¡ú Name: func1(s=0x7ffff7dd4e80 <initial> "")
[#1] 0x4006ef ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc40:	0xffffdc80	0x00007fff	0x004006ef	0x00000000
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
gef7Ì2  c
Continuing.

Breakpoint 10, 0x0000000000400669 in func1 (s=0x7fffffffdc68 "@\005@") at functest.c:11
11	    memcpy(a,s,20);
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc30      ¡ú  0x00007fff61616161
$rbx   : 0x0               
$rcx   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rdx   : 0x14              
$rsp   : 0x7fffffffdc20      ¡ú  0x0000000000400790  ¡ú  0x0070252073692070 ("p is %p"?)
$rbp   : 0x7fffffffdc40      ¡ú  0x00007fffffffdc80  ¡ú  0x0000000000000000
$rsi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rdi   : 0x7fffffffdc30      ¡ú  0x00007fff61616161
$rip   : 0x400669            ¡ú  <func1+60> call 0x400530 <memcpy@plt>
$r8    : 0x7ffff7b8b640      ¡ú  "0123456789abcdefghijklmnopqrstuvwxyz"
$r9    : 0x0               
$r10   : 0x7ffff7dd26a0      ¡ú  0x0000000000000000
$r11   : 0x0               
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry parity adjust zero sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc20©¦+0x00: 0x0000000000400790  ¡ú  0x0070252073692070 ("p is %p"?)	 ¡û $rsp
0x00007fffffffdc28©¦+0x08: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc30©¦+0x10: 0x00007fff61616161	 ¡û $rax, $rdi
0x00007fffffffdc38©¦+0x18: 0x00000004f7ffe1c8
0x00007fffffffdc40©¦+0x20: 0x00007fffffffdc80  ¡ú  0x0000000000000000	 ¡û $rbp
0x00007fffffffdc48©¦+0x28: 0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798
0x00007fffffffdc50©¦+0x30: "aaaaaaaaaaaaaaaaaaaa"
0x00007fffffffdc58©¦+0x38: "aaaaaaaaaaaa"
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x40065d <func1+48>       lock   mov edx, 0x14
     0x400663 <func1+54>       mov    rsi, rcx
     0x400666 <func1+57>       mov    rdi, rax
 ¡ú   0x400669 <func1+60>       call   0x400530 <memcpy@plt>
   6É9    0x400530 <memcpy@plt+0>   jmp    QWORD PTR [rip+0x200b0a]        # 0x601040 <memcpy@got.plt>
        0x400536 <memcpy@plt+6>   push   0x5
        0x40053b <memcpy@plt+11>  jmp    0x4004d0
        0x400540 <_start+0>       xor    ebp, ebp
        0x400542 <_start+2>       mov    r9, rdx
        0x400545 <_start+5>       pop    rsi
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ arguments (guessed) ]©¤©¤©¤©¤
memcpy@plt (
   $rdi = 0x00007fffffffdc30 ¡ú 0x00007fff61616161,
   $rsi = 0x00007fffffffdc68 ¡ú 0x0000000000400540 ¡ú <_start+0> xor ebp, ebp,
   $rdx = 0x0000000000000014,
   $rcx = 0x00007fffffffdc68 ¡ú 0x0000000000400540 ¡ú <_start+0> xor ebp, ebp
)
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+11 ]©¤©¤©¤©¤
      6	 {
      7	     char a[4];
      8	     int j;
      9	     for ( j = 0 ; j < 4; j++)
     10	 	   a[j] = 'a';
		// s=0x00007fffffffdc28  ¡ú  [...]  ¡ú  <_start+0> xor ebp, ebp, a=0x00007fffffffdc30  ¡ú  0x00007fff61616161
 ¡ú   11	     memcpy(a,s,20);
     12	 }
     13	 
     14	 void func2(void)
     15	 {
     16	     printf("hello,world\n");
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x400669 ¡ú Name: func1(s=0x7fffffffdc68 "@\005@")
[#1] 0x4006ef ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc20:	0x00400790	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc30:	0x61616161	0x00007fff	0xf7ffe1c8	0x00000004
0x7fffffffdc40:	0xffffdc80	0x00007fff	0x004006ef	0x00000000
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
gef7Ì2  c
Continuing.

Breakpoint 11, func1 (s=0x7fffffffdc68 "@\005@") at functest.c:12
12	}
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc30      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rbx   : 0x0               
$rcx   : 0xff              
$rdx   : 0x14              
$rsp   : 0x7fffffffdc20      ¡ú  0x0000000000400790  ¡ú  0x0070252073692070 ("p is %p"?)
$rbp   : 0x7fffffffdc40      ¡ú  0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rsi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rdi   : 0x7fffffffdc30      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rip   : 0x40066e            ¡ú  <func1+65> leave 
$r8    : 0x1               
$r9    : 0x1               
$r10   : 0x7fffffffd9e0      ¡ú  0x0000000000000000
$r11   : 0x7ffff7aaba30      ¡ú  <__memcpy_sse2_unaligned+0> mov rax, rsi
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc20©¦+0x00: 0x0000000000400790  ¡ú  0x0070252073692070 ("p is %p"?)	 ¡û $rsp
0x00007fffffffdc28©¦+0x08: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc30©¦+0x10: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rax, $rdi
0x00007fffffffdc38©¦+0x18: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc40©¦+0x20: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rbp
0x00007fffffffdc48©¦+0x28: 0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798
0x00007fffffffdc50©¦+0x30: "aaaaaaaaaaaaaaaaaaaa"
0x00007fffffffdc58©¦+0x38: "aaaaaaaaaaaa"
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400663 <func1+54>       mov    rsi, rcx
     0x400666 <func1+57>       mov    rdi, rax
     0x400669 <func1+60>       call   0x400530 <memcpy@plt>
 ¡ú   0x40066e <func1+65>       leave  
     0x40066f <func1+66>       ret    
     0x400670 <func2+0>        push   rbp
     0x400671 <func2+1>        mov    rbp, rsp
     0x400674 <func2+4>        mov    edi, 0x400784
     0x400679 <func2+9>        call   0x4004e0 <puts@plt>
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+12 ]©¤©¤©¤©¤
      7	     char a[4];
      8	     int j;
      9	     for ( j = 0 ; j < 4; j++)
     10	 	   a[j] = 'a';
     11	     memcpy(a,s,20);
 ¡ú   12	 }
     13	 
     14	 void func2(void)
     15	 {
     16	     printf("hello,world\n");
     17	 }
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40066e ¡ú Name: func1(s=0x7fffffffdc68 "@\005@")
[#1] 0x4006ef ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc20:	0x00400790	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc30:	0x00400540	0x00000000	0x00400670	0x00000000
0x7fffffffdc40:	0xffffdc68	0x00007fff	0x004006ef	0x00000000
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
gef7Ì2  c
Continuing.

Breakpoint 12, 0x000000000040066f in func1 (s=0x7fffffffdc68 "@\005@") at functest.c:12
12	}
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x7fffffffdc30      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rbx   : 0x0               
$rcx   : 0xff              
$rdx   : 0x14              
$rsp   : 0x7fffffffdc48      ¡ú  0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798
$rbp   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rsi   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rdi   : 0x7fffffffdc30      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rip   : 0x40066f            ¡ú  <func1+66> ret 
$r8    : 0x1               
$r9    : 0x1               
$r10   : 0x7fffffffd9e0      ¡ú  0x0000000000000000
$r11   : 0x7ffff7aaba30      ¡ú  <__memcpy_sse2_unaligned+0> mov rax, rsi
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc48©¦+0x00: 0x00000000004006ef  ¡ú  <main+85> mov edi, 0x400798	 ¡û $rsp
0x00007fffffffdc50©¦+0x08: "aaaaaaaaaaaaaaaaaaaa"
0x00007fffffffdc58©¦+0x10: "aaaaaaaaaaaa"
0x00007fffffffdc60©¦+0x18: 0x0000000061616161 ("aaaa"?)
0x00007fffffffdc68©¦+0x20: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rbp, $rsi
0x00007fffffffdc70©¦+0x28: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc78©¦+0x30: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc80©¦+0x38: 0x0000000000000000
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x400666 <func1+57>       mov    rdi, rax
     0x400669 <func1+60>       call   0x400530 <memcpy@plt>
     0x40066e <func1+65>       leave  
 ¡ú   0x40066f <func1+66>       ret    
   6É9    0x4006ef <main+85>        mov    edi, 0x400798
        0x4006f4 <main+90>        call   0x4004e0 <puts@plt>
        0x4006f9 <main+95>        mov    eax, 0x0
        0x4006fe <main+100>       leave  
        0x4006ff <main+101>       ret    
        0x400700 <__libc_csu_init+0> push   r15
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+12 ]©¤©¤©¤©¤
      7	     char a[4];
      8	     int j;
      9	     for ( j = 0 ; j < 4; j++)
     10	 	   a[j] = 'a';
     11	     memcpy(a,s,20);
 ¡ú   12	 }
     13	 
     14	 void func2(void)
     15	 {
     16	     printf("hello,world\n");
     17	 }
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x40066f ¡ú Name: func1(s=0x7fffffffdc68 "@\005@")
[#1] 0x4006ef ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc48:	0x004006ef	0x00000000	0x61616161	0x61616161
0x7fffffffdc58:	0x61616161	0x61616161	0x61616161	0x00000000
0x7fffffffdc68:	0x00400540	0x00000000	0x00400670	0x00000000
0x7fffffffdc78:	0xffffdc68	0x00007fff	0x00000000	0x00000000
0x7fffffffdc88:	0xf7a32f45	0x00007fff	0x00000000	0x00000000
0x7fffffffdc98:	0xffffdd68	0x00007fff	0x00000000	0x00000001
0x7fffffffdca8:	0x0040069a	0x00000000	0x00000000	0x00000000
0x7fffffffdcb8:	0x3758b263	0x1a844df6	0x00400540	0x00000000
0x7fffffffdcc8:	0xffffdd60	0x00007fff	0x00000000	0x00000000
0x7fffffffdcd8:	0x00000000	0x00000000	0x8e78b263	0xe57bb209
gef7Ì2  c
Continuing.
p is 0x400670really!

Breakpoint 1, main () at functest.c:44
44	}
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x0               
$rbx   : 0x0               
$rcx   : 0x7ffff7b003c0      ¡ú  <__write_nocancel+7> cmp rax, 0xfffffffffffff001
$rdx   : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$rsp   : 0x7fffffffdc50      ¡ú  "aaaaaaaaaaaaaaaaaaaa"
$rbp   : 0x7fffffffdc68      ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
$rsi   : 0x7ffff7ff7000      ¡ú  "p is 0x400670really!"
$rdi   : 0x1               
$rip   : 0x4006fe            ¡ú  <main+100> leave 
$r8    : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$r9    : 0x1               
$r10   : 0x7fffffffda10      ¡ú  0x0000000000000000
$r11   : 0x246             
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc50©¦+0x00: "aaaaaaaaaaaaaaaaaaaa"	 ¡û $rsp
0x00007fffffffdc58©¦+0x08: "aaaaaaaaaaaa"
0x00007fffffffdc60©¦+0x10: 0x0000000061616161 ("aaaa"?)
0x00007fffffffdc68©¦+0x18: 0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp	 ¡û $rbp
0x00007fffffffdc70©¦+0x20: 0x0000000000400670  ¡ú  <func2+0> push rbp
0x00007fffffffdc78©¦+0x28: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc80©¦+0x30: 0x0000000000000000
0x00007fffffffdc88©¦+0x38: 0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x4006ef <main+85>        mov    edi, 0x400798
     0x4006f4 <main+90>        call   0x4004e0 <puts@plt>
     0x4006f9 <main+95>        mov    eax, 0x0
 ¡ú   0x4006fe <main+100>       leave  
     0x4006ff <main+101>       ret    
     0x400700 <__libc_csu_init+0> push   r15
     0x400702 <__libc_csu_init+2> mov    r15d, edi
     0x400705 <__libc_csu_init+5> push   r14
     0x400707 <__libc_csu_init+7> mov    r14, rsi
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+44 ]©¤©¤©¤©¤
     39	     printf("p is %p",p);
     40	     s = s + 24;
     41	     func1(s);
     42	     printf("really!\n");
     43	     return 0;
 ¡ú   44	 }
     45	 
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x4006fe ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef7Ì2  x /40x $rsp
0x7fffffffdc50:	0x61616161	0x61616161	0x61616161	0x61616161
0x7fffffffdc60:	0x61616161	0x00000000	0x00400540	0x00000000
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdce0:	0x8e78b263	0xe57bb209	0x6aa2b263	0xe57ba2b0
gef  si

Breakpoint 2, 0x00000000004006ff in main () at functest.c:44
44	}
[ Legend: Modified register | Code | Heap | Stack | String ]
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ registers ]©¤©¤©¤©¤
$rax   : 0x0               
$rbx   : 0x0               
$rcx   : 0x7ffff7b003c0      ¡ú  <__write_nocancel+7> cmp rax, 0xfffffffffffff001
$rdx   : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$rsp   : 0x7fffffffdc70      ¡ú  0x0000000000400670  ¡ú  <func2+0> push rbp
$rbp   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$rsi   : 0x7ffff7ff7000      ¡ú  "p is 0x400670really!"
$rdi   : 0x1               
$rip   : 0x4006ff            ¡ú  <main+101> ret 
$r8    : 0x7ffff7dd59e0      ¡ú  0x0000000000000000
$r9    : 0x1               
$r10   : 0x7fffffffda10      ¡ú  0x0000000000000000
$r11   : 0x246             
$r12   : 0x400540            ¡ú  <_start+0> xor ebp, ebp
$r13   : 0x7fffffffdd60      ¡ú  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$es: 0x0000  $cs: 0x0033  $ds: 0x0000  $gs: 0x0000  $fs: 0x0000  $ss: 0x002b  
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ stack ]©¤©¤©¤©¤
0x00007fffffffdc70©¦+0x00: 0x0000000000400670  ¡ú  <func2+0> push rbp	 ¡û $rsp
0x00007fffffffdc78©¦+0x08: 0x00007fffffffdc68  ¡ú  0x0000000000400540  ¡ú  <_start+0> xor ebp, ebp
0x00007fffffffdc80©¦+0x10: 0x0000000000000000
0x00007fffffffdc88©¦+0x18: 0x00007ffff7a32f45  ¡ú  <__libc_start_main+245> mov edi, eax
0x00007fffffffdc90©¦+0x20: 0x0000000000000000
0x00007fffffffdc98©¦+0x28: 0x00007fffffffdd68  ¡ú  0x00007fffffffe112  ¡ú  "/home/zpy/devel/test/functest/func"
0x00007fffffffdca0©¦+0x30: 0x0000000100000000
0x00007fffffffdca8©¦+0x38: 0x000000000040069a  ¡ú  <main+0> push rbp
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ code:i386:x86-64 ]©¤©¤©¤©¤
     0x4006f4 <main+90>        call   0x4004e0 <puts@plt>
     0x4006f9 <main+95>        mov    eax, 0x0
     0x4006fe <main+100>       leave  
 ¡ú   0x4006ff <main+101>       ret    
   6É9    0x400670 <func2+0>        push   rbp
        0x400671 <func2+1>        mov    rbp, rsp
        0x400674 <func2+4>        mov    edi, 0x400784
        0x400679 <func2+9>        call   0x4004e0 <puts@plt>
        0x40067e <func2+14>       pop    rbp
        0x40067f <func2+15>       ret    
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ source:functest.c+44 ]©¤©¤©¤©¤
     39	     printf("p is %p",p);
     40	     s = s + 24;
     41	     func1(s);
     42	     printf("really!\n");
     43	     return 0;
 ¡ú   44	 }
     45	 
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ threads ]©¤©¤©¤©¤
[#0] Id 1, Name: "func", stopped, reason: BREAKPOINT
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤[ trace ]©¤©¤©¤©¤
[#0] 0x4006ff ¡ú Name: main()
©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤©¤
gef  x /40x $rsp
0x7fffffffdc70:	0x00400670	0x00000000	0xffffdc68	0x00007fff
0x7fffffffdc80:	0x00000000	0x00000000	0xf7a32f45	0x00007fff
0x7fffffffdc90:	0x00000000	0x00000000	0xffffdd68	0x00007fff
0x7fffffffdca0:	0x00000000	0x00000001	0x0040069a	0x00000000
0x7fffffffdcb0:	0x00000000	0x00000000	0x3758b263	0x1a844df6
0x7fffffffdcc0:	0x00400540	0x00000000	0xffffdd60	0x00007fff
0x7fffffffdcd0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdce0:	0x8e78b263	0xe57bb209	0x6aa2b263	0xe57ba2b0
0x7fffffffdcf0:	0x00000000	0x00000000	0x00000000	0x00000000
0x7fffffffdd00:	0x00000000	0x00000000	0x00400700	0x00000000
gef i r
rax            0x0	0x0
rbx            0x0	0x0
rcx            0x7ffff7b003c0	0x7ffff7b003c0
rdx            0x7ffff7dd59e0	0x7ffff7dd59e0
rsi            0x7ffff7ff7000	0x7ffff7ff7000
rdi            0x1	0x1
rbp            0x400540	0x400540 <_start>
rsp            0x7fffffffdc70	0x7fffffffdc70
r8             0x7ffff7dd59e0	0x7ffff7dd59e0
r9             0x1	0x1
r10            0x7fffffffda10	0x7fffffffda10
r11            0x246	0x246
r12            0x400540	0x400540
r13            0x7fffffffdd60	0x7fffffffdd60
r14            0x0	0x0
r15            0x0	0x0
rip            0x4006ff	0x4006ff <main+101>
eflags         0x246	[ PF ZF IF ]
cs             0x33	0x33
ss             0x2b	0x2b
ds             0x0	0x0
es             0x0	0x0
fs             0x0	0x0
gs             0x0	0x0
gef  c
Continuing.
hello,world

```




