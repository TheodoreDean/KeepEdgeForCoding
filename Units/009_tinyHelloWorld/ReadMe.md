###-== tinyhelloworld ==-###

###compile and link
> gcc -m32 -c -fno-builtin tinyhelloworld.c //complie x86 code
> ld -m elf_i386 -static -e nomain -o targethelloworld tinyhelloworld.o



