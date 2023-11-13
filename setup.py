# For info on how to write a setup.py file, check out the link below 
# or ask a friendly neighborhood python programmer! 
# https://docs.python.org/3.7/distutils/setupscript.html

from setuptools import setup, find_packages
import glob

setup(
    name = "ullyses_utils",
    version = "0.0.1",
    description = "ULLYSES utility files and scripts",
    author = "ULLYSES STScI Team",
    keywords = ["astronomy", "jwst", "simulations", "etc"],
    classifiers = ['Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Science/Research',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
    packages = ["ullyses_utils"],
    package_dir = {"ullyses_utils": "utils"},
    package_data = {"ullyses_utils": ["data/cos_shifts/*",
                                      "data/lcogt_catalogs/*", 
									  "data/lcogt_photometry/*",
								      "data/ref_files/*",
								      "data/stis_configs/*",
								      "data/target_metadata/*",
								      "data/vignette_scaling/*",
								      "data/fuse/*",
								      "data/calibration_metadata/*",
								      "data/timeseries/*"
									]},
    install_requires = ["setuptools",
                        "numpy",
                        "astropy",
                        ],
    )

