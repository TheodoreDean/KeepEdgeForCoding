
/*
 longestSubstring.c

 *

 *  Created on: 2018年3月15日

 *      Author: Pengyizhan

 * Question

 *Given a string, find the length of the longest substring without repeating characters.

 *Examples:

 *Given "abcabcbb", the answer is "abc", which the length is 3.

 *Given "bbbbb", the answer is "b", with the length of 1.

 *Given "pwwkew", the answer is "wke", with the length of 3. Note that the answer must be a substring, "pwke" is a subsequence and not a substring.

 */



#include <stdio.h>

#include <stdlib.h>

#include "longestSubstring.h"



int lengthOfLongestSubstring(char* s)

{

	int len=0;

    char *end=s,*temp;

	char* addressTable[128]={NULL};



	while(*end){

		printf("end is %s\n s is %s \n*end is %c\n",end,s,*end);

		temp = addressTable[*end];//treat the ascii as the index of the array

		addressTable[*end]=end;//assign the array[ascii]

		printf("temp is %s \n addressTable[*end] is %s\n",temp,addressTable[*end]);

		if(temp>=s){// if the temp string is equal or include the s string

		printf("end is %d\n s is %d \n",end,s);

		len=end-s>len?end-s:len;

		s = temp+1;

		}end++;

	}

	printf("finals : end is %d\n s is %d \n",end,s);

	len=end-s>len?end-s:len;

	return len;

}

/*

 *end is the character’s ascii number,
 *and we use the ascii number as the index of addressTable
 *what stored in the addressTable is the character’s address
 *At first, every pointer in addressTable is initialized as NULL
 *and pointer s and end are at the start of the string
 *As the while clause proceeds, the pointer end ‘register’ every character(of that string)'s address into the addressTable of the index(which is the exact ascii number of that character)
 *when end encounters a same ascii number , the if clause will handle this
 *what the if clause will do is recording the length of current substring(specified between s and end, calculated by end-s) and then update s to temp+1
 *temp stores the older same character’s address

*/
