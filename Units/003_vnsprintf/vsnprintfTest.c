#include <stdio.h>  
#include <stdarg.h>  
  
void SYSTEM(const char * format, ...)  
{  
    char buff[4069];  
    va_list list;  
    va_start(list, format);  
    vsnprintf(buff, 4069, format, list);  
    va_end(list);  
    printf("%s\n", buff);  
}  
  
void main()  
{  
    SYSTEM("%d+++++%s++++++%d",1,"&",1);  
}
/*
vsnprintf函数
头文件：#include  <stdarg.h>
函数原型：int vsnprintf(char *str, size_t size, const char *format, va_list ap);
函数说明：将可变参数格式化输出到一个字符数组
参数：
str输出到的数组，size指定大小，防止越界，format格式化参数，ap可变参数列表函数用法

STSTEM()以“%d+%s+%d”的形式传入数据并打印

*/
