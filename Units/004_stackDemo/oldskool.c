#include <string.h>
#include <stdio.h>
void go(char *data){

	char name[8];
	strcpy(name,data);
	printf("Winner is : %s\n",name);
}

int main (int argc, char **argv){
	go(argv[1]);
}

void nasty(){
	printf("a little nasty\n");
}
