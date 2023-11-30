# ullyses-utils

## About

This repository contains utility scripts and data files for use in the ULLYSES program.

## Installation

To use the utility scripts and files in this repository, simply install like so:
```
pip install ullyses-utils
```
## Usage

### Utility Scripts
This repo houses several utility scripts that are needed to creates ULLYSES HLSPs. Most are specific to this purpose, but some may be generally useful: specific functions in such scripts are described below.

**`match_aliases.match_aliases`**

Given an input target name, an attempt is made to match it to any aliases in the ULLYSES sample.
By default, this returns the matched HLSP name, which is the target name used in ULLYSES products. You may alternatively specify that the ULLYSES name (generally recognized target name, with special characters) or the SIMBAD name (target name resolvable by SIMBAD) be returned instead.

```
from match_aliases import match_aliases
match_aliases("BAT99 105")
match_aliases("BAT99 105", return_name="target_name_ullyses")
match_aliases("BAT99 105", return_name="target_name_simbad")
```

### Utility data files

To use the utility data files, the package should be imported and then relative paths can be determined from your local installation.
For example, if you wish to reference the ULLYSES target alias file, you would do so like this:
```
import os
import ullyses_utils
local_dir = ullyses_utils.__path__[0]
alias_file = os.path.join(local_dir, "data/target_metadata/pd_all_aliases.json")
```
