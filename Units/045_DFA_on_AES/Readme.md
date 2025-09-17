###  DFA on AES 128


#### Preconditions

> 1. fault injection tools

> 2. oscilloscope pico-3000 to analyis the AES 9th round encryption.

> 3. Install JupyterLab by pip and configure the JDK correctly.

#### Steps 


> 1. Create the fault during AES 9th operation.

> 2. Collect enough fault ciphertext with at least 4 pairs.

```
The wrong byte should be in this way.

|x| | | |    | |x| | |    | | |x| |    | | | |x|
| | | |x|    |x| | | |    | |x| | |    | | |x| |
| | |x| |    | | | |x|    |x| | | |    | |x| | |
| |x| | |    | | |x| |    | | | |x|    |x| | | |


```
> 3. Using the script to reconstitute the master key(1st round  key) by reversing the key schedule.


#### Notes

> 1. The fault glitch_pulse time(normally (10~12)*10ns) should be accurate enough to trigger a crash. Only under these circumstances it is feasible to inject a fault during AES encryption. So the glitch_pluse time should be enumerated to discover the most suitable one.

> 2. The fault glitch_delay time should be the 9th AES round operation. It can be oberserved by the Oscilloscope.

> 3. Guidance can be found in [https://yichen115.github.io/%E4%B8%8A%E6%89%8B%E6%8C%87%E5%8D%97/PowerShorter%E5%BC%80%E7%AE%B1%E4%B8%8E%E7%AE%80%E5%8D%95%E4%BD%BF%E7%94%A8/]



