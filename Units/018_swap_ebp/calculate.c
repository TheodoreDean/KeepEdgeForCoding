#include <stdio.h>
#include <string.h>
int main(){
	char buf[1024];
	int a,b,res;
	char *mystr = "Calculateing...\n ";
	char *emsg = "Error in adding \n";

	a = 5;
	b = 10;
	mywrite(1,mystr,strlen(mystr));
	if (myadd(a,b,&res)){
		sprintf(buf,"The result is %d\n", res);
		mywrite(1,buf,strlen(buf));
	}else {
		mywrite(1,emsg,strlen(emsg));
	}
	return 0;
}
