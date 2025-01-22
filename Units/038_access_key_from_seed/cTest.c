#include<stdio.h>
#include<string.h>


int main () {

char *seed=0x0c060003;
//char *seed=;
//printf("seed is %u ", *seed);

unsigned int param1= 0x0C060003;
unsigned int param2= 0xeda7;

unsigned int local_c;

local_c = param1^param2;

printf("first stage unsigned int local_c is %u",local_c);

for (int i=0 ; i<32; i++){
    local_c = (local_c <<7 | local_c >> 0x19) ^ param2;
}

printf("unsigned int local_c before & is %u ", local_c);

local_c = local_c & 0xFFFFFF00;

printf("unsigned int local_c  after & is %u ", local_c);


//unsigned int concatSeed = (unsigned int)strcat(*seed,*addSeed);

//printf("concatSeed is %u ", concatSeed);


//char newchar = (char)seed;

//char Eightchar = (char)((unsigned int)seed >> 8);

//printf("8 bit  testseed is %c ", Eightchar);



printf("\n");




return 0;
}
