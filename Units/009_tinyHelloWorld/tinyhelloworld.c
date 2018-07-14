char* str = "hello world！/\n";

void print ()
{
/* 
	int write(int filedesc, char* buffer,int size);
	pass the parameters by using eax ebx edx;
	WRITE的调用号为4 eax = 4
	filedesc represents the file be writen, in this scenerio, the default stdout is used. so the handle is NULL, ebx = 0;
        buffer is the soucebuffer so ecx = str;
	size of "helloworld\n "is 13, so edx = 13;
 */
	asm("movl $13, %%edx \n\t"
	    "movl %0,%%ecx \n\t"
	    "movl $0,%%ebx \n\t"
	    "movl $4,%%eax \n\t"
	    "int $0x80 \n\t"
	    ::"r"(str):"edx","ecx","ebx");
} 

void exit ()
{
	asm ("movl $42, %ebx \n\t"
	     "movl $1,%eax \n\t"
  	     "int $0x80 \n\t");
}


void nomain()
{
	print();
	exit();
}
