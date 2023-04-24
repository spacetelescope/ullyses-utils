# FUSE Inputs

We use these data products in conjunction with the ULLYSES pipeline to get the final FUSE high level science product.

## YAML files
The following configuration files are used in the ULLYSES HLSP pipeline:
- bad_fuse_targs.yaml
  - A list of FUSE targets that should not be included due to data quality issues. Not used in the pipeline, but instead for bookkeeping.
- fuse_dq_flagging.yaml
  - A list of custom DQ flags to add to the FUSE HLSPs.
    - DQ=1 (Worm)
    - DQ=2 (Poor photometric quality)
    - DQ=4 (Rescaled flux, i.e. anything updated in the jupyter notebooks below.)
- good_fuse_targs.yaml
  - List of all FUSE targets by DR. Commented lines are targets that had serious data quality issues and were not included in the DR.

## Jupyter Notebooks
All archival FUSE data used in the ULLYSES sample are examined and vetted by the ULLYSES team. Some targets exhibit various issues in their spectra, such as spectral channel drifting. In DR6, the ULLYSES team has begun to deliver improved spectra for such targets. Using the strategy outlined below, FUSE data for 23 targets previously excluded from the sample were able to be rectified and included in products. The notebooks included in this repository follow the procedure below. Needed in the directory where the notebook is run is the corresponding "all" file for the dataset rootname listed at the beginning of the notebook. Each notebook also includes notes specific to each target, as they each require slightly different modifications.

The following strategy was used to repair these data:
1. Begin by examining the NVO file, which was initially created by splicing together pieces of the extracted spectra from the eight FUSE detector segments.
  - If the NVO file does not meet data quality needs (e.g., depressed flux or mismatching flux at channel transition points), a new NVO file is created by using the eight individual extracted spectra in the “ALL” files. These eight spectra are shifted to a common wavelength zero point and rescaled to create a new NVO file.
2. The guide channel is identified (LiF1A for the first half of the mission, and LiF2A for the second) and its spectrum adopted as a reference.
3. If the spectra from other channels are less than 50% brighter than the reference, then they are rescaled to match the reference in the region of overlap.
4. If they are more than 50% brighter than the reference, they are assumed to be contaminated by nearby stars and not included in the final spectrum.

Even with these corrections, some flux mismatches still remain at the transition point between FUSE and HST data- these are not corrected by the ULLYSES team. If smooth transitions are required, one of the contributing spectra may be manually scaled to the other.

Updated targets for DR6:
- 2dfs-999_g0390501.ipynb
- av235_p1030301.ipynb
- av267_e5110701.ipynb
- av26_p1176001.ipynb
- av388_p1175401.ipynb
- av39a_g0390301.ipynb
- av476_c0020301.ipynb
- av83_p1176201.ipynb
- bat99-105_d0981701.ipynb
- bi272_p1172902.ipynb
- lh114-7_d0981101.ipynb
- lmcx-4_a0440102.ipynb
- moa-j010321-720538_f3210102.ipynb
- ngc2004-els-26_d1380301.ipynb
- ngc346-mpg-342_p2030401.ipynb
- ngc346-mpg-355_p2030301.ipynb
- pgmw-3070_b0100201.ipynb
- sk-65d55_g9270501.ipynb
- sk-67d104_p1031302.ipynb
- sk-67d106_a1110101.ipynb
- sk-67d168_b0860901.ipynb
- sk-68d16_e5112201.ipynb
- sk-70d13_d0981001.ipynb

Updated targets for DR7:
- ngc346-mpg-435_p2030201.ipynb
