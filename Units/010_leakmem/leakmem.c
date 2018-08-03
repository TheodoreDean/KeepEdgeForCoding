#include <stdio.h>
int main() {

// #1
  char s[100];
  int a = 1, b = 0x22222222, c = -1;
  scanf("%s", s);
  printf("%08x.%08x.%08x.%s\n", a, b, c, s);
  printf(s);

#if 0
// #2
  char s[100] = {'A','A','A'}; 
  printf("%3$s", 1, 2, s, 4);
#endif 
  return 0;
}

