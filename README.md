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
from ullyses_utils.match_aliases import match_aliases
match_aliases("BAT99 105")
match_aliases("BAT99 105", return_name="target_name_ullyses")
match_aliases("BAT99 105", return_name="target_name_simbad")
```

**`select_pids.select_all_pids`**

For of the two main categories the ULLYSES sample (high mass and low mass T-Tauri stars), this function can be used to obtain all of the program IDs (PIDs) associated with each of the categories. There are also options to include or not include the extra stars in the sample, i.e. archival data from stars that were added after the original sample was created, and an option to include the monitoring T-Tauri star targets or not. Additionally, you can separate out the ULLYSES observed PIDs and any ARCHIVAL PIDs using the option `single_list=False`. Otherwise, this function returns a list of all PIDs for the parameters specified.

A few examples of using this function include:
1) For massive stars (LMC, SMC, lowz).
```
from ullyses_utils.select_pids import select_all_pids
massive_pids = select_all_pids(massive=True)
```
2) For the original set of massive stars (LMC, SMC, lowz).
```
from ullyses_utils.select_pids import select_all_pids
no_extra_pids = select_all_pids(massive=True, extra=False)
```
3) For all stars in the t-tauri star sample, including the monitoring stars.
```
from ullyses_utils.select_pids import select_all_pids
tts_pids = select_all_pids(tts=True)
```
4) For only the stars in the classic t-tauri star sample
```
from ullyses_utils.select_pids import select_all_pids
classic_tts_pids = select_all_pids(tts=True, monitoring=False)
```
5) For all stars in the ULLYSES sample
```
from ullyses_utils.select_pids import select_all_pids
all_pids = select_all_pids()
```
6) To separate out ULLYSES observed and archival data
```
from ullyses_utils.select_pids import select_all_pids
all_pids_dict = select_all_pids(single_list=False)
```

**`select_pids.select_pids`**

Used by `select_all_pids`, this function allows for more granularity in what PIDs are being selected based on specific regions. By default, all PIDs are returned as a single list unless the parameter `single_list=False`, then a list of archival PIDs and ULLYSEs observed PIDS are returned. The accepted regions to search are:
 - "smc-extra", "smc",
 - "lmc-extra", "lmc",
 - "lowz-extra", "lowz-image", "lowz",
 - "monitoring_tts",
 - "cha i", "cra", "eps cha", "eta cha", "lupus", "ori ob", "sigma ori", "taurus", "twa", "lower centaurus", "upper scorpius", "other", "lambda orionis"

```
from ullyses_utils.select_pids import select_pids
orig_lmc_pids = select_pids("lmc")
all_lmc_pids = select_pids("lmc") + select_pids("lmc-extra")
ullyses_mon_pids, archival_mon_pids = select_pids("monitoring_tts", single_list=False)
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
