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



