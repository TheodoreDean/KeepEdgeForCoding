### Interesting finds on Ubuntu 18.04.1 

## Wrong setting lead to  dead-lock login process

>  When setting varibale in /etc/profile
>  for instance, when using cmake  or gcc-arm-none-eabi  toolchains by setting the system variable

```
export PATH=$path:$/to/ur/dir/bin/

```
> the second "path" is CAPITAL sensitive.
> if the error occurs like above, it will fall in dead end loop when login the system after rebooting it.

## The orders of the setting sentence matters

> for instance  

```
export PATH=/TO/UR/DIR/BIN/:$PATH

export PATH=$PATH:$/TO/UR/DIR/BIN/
```

> When typing 

```
echo  $PATH
```

> The order of two settings( PATH ) are different. Sometimes it may have bad influence on compiling project.

> So basically order matters!!!


