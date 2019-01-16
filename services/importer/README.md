# Database Export

## Running Script

```bash
./test.py --key=acbd18db4cc2f85cedef654fccc4a4d8 --apikey=fdba98970961edb2
```

## Setting Default Keys

**Add keys**

Create a file in this directory: `api_keys.sh`

```bash
#!/usr/bin/env bash
export CIVICRM_KEY=acbd18db4cc2f85cedef654fccc4a4d8
export CIVICRM_APIKEY=fdba98970961edb2
```

Note: the above keys are made up, so replace them with actual keys

**Run Script**

```bash
source api_keys.sh
./test.py
```
