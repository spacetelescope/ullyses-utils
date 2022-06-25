# ullyses-utils

## About

This repository contains utility scripts and data files for use in the ULLYSES program.

## Installation

To use the utility scripts and files in this repository, simply install like so:
```
python setup.py install
```

If another package requires files or scripts in this utils repo, you can add a dependence in the `setup.py` file like so:
```
setup(...
      install_requires = ["ullyses_utils"],
      dependency_links = ["git+https://github.com/spacetelescope/ullyses-utils@main#egg=ullyses_utils-<version>"])
```
where `<version>` is the version of the ullyses-utils package you desire.

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
alias_file = os.path.join(local_dir, "data/target_metadata/pd_all_aliases.json")
```
