//
//  main.cpp
//  findPalindromicSubstring
//
//  Created by CTTL-IFS on 2018/4/20.
//  Copyright © 2018年 CTTL-IFS. All rights reserved.
//

#include <iostream>
#include "findPalindromicStr.hpp"

int main(int argc, const char * argv[]) {
    // insert code here...
    std::cout << "Hello, World!\n";
    string str1 = "abcbabcdcba",str2,str3;
    //str2 = preProcess(str1);
    str3 = longestPalindrome(str1);
    //printf("%s\n",str3.c_str());
    cout << str3;
    return 0;
}
