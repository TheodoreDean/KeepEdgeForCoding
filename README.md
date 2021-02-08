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

>![find the substrings](https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/002_longestSubstring/A7A03F11-2D2A-49B5-B443-1F85C5C644F5.png)
```
//use the ascii number as the index of addressTable

temp = addressTable[*end];//treat the ascii as the index of the array
addressTable[*end]=end;//assign the array[ascii]

```
***
### 005 find palindromic substrings
> find the longest palindromic substrings

> essence of the code
```
if P[ i’ ] ≤ R – i,
then P[ i ] ← P[ i’ ]
else P[ i ] ≥ P[ i’ ]. (Which we have to expand past the right edge (R) to find P[ i ].

```

Please find the manacher's algorithm as below:

[https://articles.leetcode.com/longest-palindromic-substring-part-ii/]

[http://www.felix021.com/blog/read.php?2040]

### 006 palindrome number
> Determine whether an integer is a palindrome. An integer is a palindrome when it reads the same backward as forward.
```
 while(x > revertedNumber)
    {
        revertedNumber = revertedNumber * 10 + (x % 10);
        x /= 10;
    }
```
> Integer Overflow

### 008 getopt demo
> simple example of getopt() and extern char* optarg;
                                 extern int optind;
                                 extern int opteer;
                                 extern int optopt;
```
while ((oc = getopt(argc,argv,"pxl:h")) != -1)
	{ switch(oc)
          {
            case 'a':
            case 'b':
            ...
            case '?':
           }
      }
```
More descriptions:
[https://blog.csdn.net/men_wen/article/details/61934376]
[https://blog.csdn.net/huangxiaohu_coder/article/details/7475156]

### 009 tinyhelloworld
> the c code without main() and header file
> Please find details as below:

[https://github.com/TheodoreDean/KeepEdgeForCoding/blob/master/Units/009_tinyHelloWorld/ReadMe.md]

### 010 leakmemory
> basic leak of memory by printf(), alternative funcations such as fprintf, vprintf,vsnprintf,and so on

> please find details as below:

[https://ctf-wiki.github.io/ctf-wiki/pwn/linux/fmtstr/fmtstr_exploit/]

### 014 stackoverflow $ebp
> By modify the $ebp of the main() intend to run the "unexpected" code

> please find details as below:

[https://github.com/TheodoreDean/KeepEdgeForCoding/tree/master/Units/014_ebpOverflow/Readme.md]

### 017 hping3 commands and attack script
> By manipulating the packets to create attack scenarions

> Please find it as below:
[https://github.com/TheodoreDean/KeepEdgeForCoding/tree/master/Units/017_hping3_testscript]
