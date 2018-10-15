
#include <stdio.h>
#include <string.h>

void func1(char *s)
{
    char a[4];
    int j;
    for ( j = 0 ; j < 4; j++)
	   a[j] = 'a'; 
    memcpy(a,s,20);
}

void func2(void)
{
    printf("hello,world\n");
}

void func3(char *s)
{
    func1(s);
}

int main(void)
{
    void (*p)(void);
    char a[20] ;
    char *s = a;
    memset(a,'a',20);
    
#if 0 
    for(i = 0; i < 8; i++)
	    //a[i] = 0;
            a[i] = '\0';
    
#endif
    
    p = func2;
    printf("p is %p",p);
    s = s + 24;
    func1(s);
    printf("really!\n");
    return 0;
}

