# ullyses-utils

## Installation

To use the utility scripts and files in this repository, simply install like so:
```
python setup.py install
```

## Usage

To use the utility scripts, the module need only be imported and run:
```
from ullyses_utils import ullyses_config
```

To use the utility data files, the package should be imported and then relative paths can be determined from your local installation.
For example, if you wish to reference the ULLYSES target alias file, you would do so like this:
```
import os
import ullyses_utils
local_dir = ullyses_utils.__path__[0]
alias_file = os.path.join(local_dir, "data/target_metadata/pd_all_aliases.json"
```
