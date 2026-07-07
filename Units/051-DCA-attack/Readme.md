### Tailor for the 1 round 

> 1. Collect tailored 1-round trace and collect multiple times
```


export STALKER_SCRIPT=Stalker0-tailor.js
python Tracer.py -l libnative-lib.so -i 0x4CAC Crypto500


```
> transfer to TraceGragh formatting

```
python3 TracerGrindConvertor-Dense.py --glob 'StalkerTrace[8c5c03939dfa4bf4d01e8624d18b8078].trace'

./sqlitetrace vStalkerTrace\[8c5c03939dfa4bf4d01e8624d18b8078\].trace 8c5c03939dfa4bf4d01e8624d18b8078trace.db


```



>2. Discover which register may have leakage.

```
python3 scan_reg_byte_top_key0.py \
  --daredevil /Users/pengyi/gitDir/Daredevil/daredevil \
  --glob 'StalkerTrace*.trace' \
  --work-dir ./daredevil_scan_rb \
  --expected 0x6c


```



>3. Recover the key 
```

python3 dense_trace_to_daredevil.py \
  --glob 'StalkerTrace*.trace' \
  --out-dir ./daredevil_pack \
  --bytenum all \
  --nsamples 120000 \
  --reg 2 \
  --byte 0

/Users/pathToDaredevil/daredevil -c ./daredevil_pack/daredevil.config
