#include <stdio.h>
#include <unistd.h>

void usage(char *program)
{
        printf("Usage: %s <options> \n", program);
        printf("\n");
        printf("options:\n");
        printf("\t-p   		     Lu xiaofeng\n");
        printf("\t-x 		     XiMen Chuixue\n");
        printf("\t-l <person>        Print the man who already ready for a fight in Forbidden City\n");
//#ifdef WITH_GP_TESTS
//      printf(" gp");
//#endif
        printf("\n");
//        printf("\t                   To run several suites, use multiple names\n");
//        printf("\t                   separated by a '+')\n");
//      printf("\t                   Default value: '%s'\n", optarg);
        printf("\t-h                 Show usage\n");
//        printf("applets:\n");
//        printf("\t--sha-perf [opts]  SHA performance testing tool (-h for usage)\n");
//        printf("\t--aes-perf [opts]  AES performance testing tool (-h for usage)\n");
//#ifdef CFG_SECURE_DATA_PATH
//      printf("\t--sdp-basic [opts] Basic Secure Data Path test setup ('-h' for usage)\n");
//#endif
        printf("\n");
}


int main (int argc, char *argv[])
{
	int oc;
	char *b_opt_arg;

	while ((oc = getopt(argc,argv,"pxl:h")) != -1)
	{
		switch(oc)
		{
			case 'p':
			  printf("my name is luxiaofeng\n");
			  break;
			case 'x':
			  printf("my name is ximenchuixue\n");
			  break;
			case 'l':
			  b_opt_arg = optarg;
			  printf("There is a full moon in the sky, %s already arrived in the Forbidden City \n",optarg);
			  break;
			case 'h':
			  usage(argv[0]);
			  return 0;
			default:
			  usage(argv[0]);
			  return -1;
		}
	}
	return 0;

}

