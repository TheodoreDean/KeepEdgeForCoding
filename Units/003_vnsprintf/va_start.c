#include <stdio.h>  
#include <stdarg.h>  
#include <string.h>  
//WIN7 64BIT  
#define PLAT_ADDRESS_SIZE 8 
/*ANSI标准形式的声明方式，括号内的省略号表示可选参数*/   
int demo( char *msg,...)   
{   
/*定义保存函数参数的结构*/  
va_list argp;   
int argno = 0;   
char *para;   
    /*argp指向传入的第一个可选参数，msg是最后一个确定的参数*/   
    va_start( argp, msg );   
    while (1)   
    {   
        para = va_arg(argp,char *);   
        if(strcmp(para,"\n")==0)break;   
        printf("Parameter #%d addr=0x%x is: %s\n", argno,para, para);   
        argno++;   
    }   
    va_end( argp );   
    /*将argp置为NULL*/  
    return 0;   
}  
int test_for_stack(int num, ...)    
{    
    int i, result = 0;    
    char *pitmp;   
    va_list ap;//这里写的什么list，（搞得好像是得到可变参数列表头一样）其实它就是个字符指针:char *   
        
    va_start(ap, num);// 这里把上面得到的字符指针，后移动4个字节，就是跳过num的内存地址    
    printf("num:%d, *ap:%d\n", num, *ap);// 这里打印下就会看出，*ap 跳过了num指向了下一个参数    
      
    pitmp = ap;   
    for (i = 0; i < num; i++)//这里num表示可变参数列表中有多少个参数（num本身算不算，由自己觉得，这里是不算入参数个数的）    
    {       
        result = va_arg(ap, int);//这里把ap往后跳过4个字节（sizeof(int)大小）指向下一个参数，返回的是当前参数（而非下一个参数）    
        printf("in for  result:%d,  *ap:%d\n", result, *ap);//这里打印下，可以看出，ap总是指向result后面的那个参数    
    }       
    va_end(ap);   
    
    return result;    
}   
  
  
  
/*测试可变参数*/   
int test_for_stack_address(int num, ...)    
{    
    int i, result = 0;    
    char *ptmp;   
    va_list ap;//这里写的什么list，（搞得好像是得到可变参数列表头一样）其实它就是个字符指针:char *   
        
    va_start(ap, num);// 这里把上面得到的字符指针，后移动4个字节，就是跳过num的内存地址    
      
      /*固定参数地址 & 值*/  
      printf("fixed parameter value:%d,address:0x%x\n", num, ap-2*PLAT_ADDRESS_SIZE);  
    printf("parameter num:%d, *ap:%d\n", num, *ap);  
      
    ptmp = ap;   
    for (i = 0; i < num; i++)   
    {   
        printf("#%d --> stack addr:0x%x,  *pitmp:%d\n",i, ptmp, *ptmp);    
        ptmp += PLAT_ADDRESS_SIZE;  
    }       
    va_end(ap);  
    
    return result;    
}   
  
/* 
1.函数栈的生长方向  
         
    1.1 测试结果1 (测试平台：WIN7 64BIT DEV-CPP) 
        <-高内存地址处  
        |---------------------------------|  
        |   最后一个可变参数              |     
        |---------------------------------|  
        |---------------------------------|  
        |   第N个可变参数                 |     -> va_arg(arg_ptr,int)后arg_ptr所指的地方, 即第N个可变参数的地址。  
                  
        |   第一个可变参数                |     -> va_start(arg_ptr,start)后arg_ptr所指的地方  即第一个可变参数的地址  
         
        |   最后一个固定参数              |     -> start的起始地址  
        |---------------------------------| 
        |---------------------------------|     -> 第 N个固定参数      
        <-低内存地址处 
         
        *调用test_for_stack_address(4,10,20,30,40)的运行结果：       
            *************test_for_stack_address************* 
            cpu address length -> int * = 8 
            cpu address length -> char * = 8 
             
            fixed parameter value:4,address:0x22fe10 
            parameter num:4, *ap:10 
            #0 --> stack addr:0x22fe18,  *pitmp:10 
            #1 --> stack addr:0x22fe20,  *pitmp:20 
            #2 --> stack addr:0x22fe28,  *pitmp:30 
            #3 --> stack addr:0x22fe30,  *pitmp:40 
2.参数的入栈顺序  
3.CPU的对齐方式  
4.内存地址的表达方式  
*/  
  
  
int table[10]={1};  
int main()  
{  
    printf("\r\n*************test_for_table_address*************\r\n");  
    printf("table[0] address = 0x%x\r\n",&table[0]);  
    printf("table[1] address = 0x%x\r\n",&table[1]);  
          
    printf("\r\n*************test_for_stack_address*************\r\n");  
    printf("cpu address length -> int * = %d\r\n",sizeof(int *));  
    printf("cpu address length -> char * = %d\r\n",sizeof(char *));  
    printf("\r\n");  
  
    test_for_stack_address(4,10,20,30,40);    
      
    test_for_stack(4,10,20,30,40);   
    demo("DEMO", "This", "is", "a", "demo!" ,"333333", "\n");  
      
    while(1);  
    return 0;  
}  
