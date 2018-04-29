force_rekey.py
===============================================
### Description ###

force_rekey.py script forces a VSD keyserver to reissue Seed, SEKs, and other primitives. The script triggers the particular Job "FORCE_KEYSERVER_UPDATE". A successful execution will emit a similar output in the stdout:
```bash
$ python force_rekey.py
Starting FORCE_KEYSERVER_UPDATE job for the 521_CATS_FIXED Organization
SUCCESS :: Re-keying Job succeeded!
```

The script could also be used as a primer on the VSPK's Job object handling.

### Version history ###
2018-04-26 - 1.0 - First version

### Usage ###
The example script has no cli parameters to handle, all the needed variables must be changed in the script body.
```
python force_rekey.py
```

### Author ###
[Roman Dodin](dodin.roman@gmail.com)
