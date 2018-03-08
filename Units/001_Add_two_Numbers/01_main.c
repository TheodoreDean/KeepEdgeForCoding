/*
 * main.c
 *
 *  Created on: 2018��3��7��
 *      Author: Pengyizhan
 */
#include <stdio.h>
#include <stdlib.h>

struct ListNode {
      int value;
      struct ListNode *next;
 };
//#if 0
struct ListNode* addTwoNumbers(struct ListNode* l1, struct ListNode* l2) {
		struct ListNode* p1 = l1;
		struct ListNode* p2 = l2;
		struct ListNode* ans = (struct ListNode*)malloc(sizeof(struct ListNode));//create an answer list
		ans->value = 0;//initialize the value
		struct ListNode* p = 0;//create a new list for the "do-while" part
		int c = 0;//set carry to 0
		while (p1 != 0 || p2 != 0 || c != 0) {//both of the list don't have the element
			if (p == 0) {//if the p list is 0, initial the p
				p = ans;
			}
			else {
				p->next = (struct ListNode*)malloc(sizeof(struct ListNode));
				p->next->value = 0;
				p = p->next;
			}
			int a = p1 != 0 ? p1->value : 0; //if p1 exists,the a is the first element's value
			int b = p2 != 0 ? p2->value : 0;
			int s = (a + b + c) % 10;//s is the
			c = (a + b + c) / 10;//c is the carry
			p->value = s;//the result is stored in the p->value
			p->next = 0;
			p1 = p1 == 0 ? 0 : p1->next;//to check if the p1 is the last element
			p2 = p2 == 0 ? 0 : p2->next;
		}
		return ans;
}
//#endif



int main () {
	struct ListNode *Result,*k1,*l2,*l3;
	k1 = (struct ListNode*) malloc (sizeof (struct ListNode));
	k1->value = 1;
	l2 = (struct ListNode*) malloc (sizeof (struct ListNode));
	l2->value = 2;
	k1 -> next = l2;
	l3 = (struct ListNode*) malloc (sizeof (struct ListNode));
	l3->value = 3;
	k1->next->next = l3;
	Result = addTwoNumbers(k1,k1);
	printf ("restult for k1 is %d %d %d\n",k1->value,k1->next->value,k1->next->next->value);
	printf ("Result's first is %d %d %d\n",Result->value,Result->next->value,Result->next->next->value);
	return 0;
}
