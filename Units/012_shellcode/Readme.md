### This code works in Linux 14.04 x64
> first of all, Read the following website

[https://blog.csdn.net/raintungli/article/details/43865041/]

> then compile the assembly code by

` nasm -f elf64 shell.asm
  ld -o shell shell.o
  objdump -d shell
`

 now you have the opcode that can be used

> then test the opcode

` gcc -o shelltest shelltest.c
 ./shelltest
`
~     
