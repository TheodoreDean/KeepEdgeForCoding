# KeepEdgeForCoding
## Some Interesting Questions and Possible Solutions

### 001 Add two numbers
> Add two numbers which is represented by linked lists
>![add two numbers](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/001_Add_two_Numbers/CB41BEFA2A6CDF54C770A6565C646A6F.jpg)
```
struct ListNode {
      int value;
      struct ListNode *next;
 };

```
Please find the detailed descriptions here 
[https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/001_Add_two_Numbers/001_Readme.md]
***

### 002 Substrings
> find the length of the longest substring without repeating characters

```
//use the ascii number as the index of addressTable

temp = addressTable[*end];//treat the ascii as the index of the array
addressTable[*end]=end;//assign the array[ascii]

```
