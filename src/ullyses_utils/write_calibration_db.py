import argparse
import os
import glob
import numpy as np
import pandas as pd

from astropy.io import fits
from astropy.time import Time

from ullyses_utils.match_aliases import match_aliases
from ullyses_utils.parse_csv import parse_database_csv
from ullyses_utils.readwrite_yaml import read_config
from ullyses_utils.select_pids import select_all_pids

#-------------------------------------------------------------------------------

def make_galaxy_dict():

    # grab the target db files to get all of the regions
    csvs, csv_dfs = parse_database_csv(target_type='all')
    galaxy_dict = {}
    for df in csv_dfs:
        # loop through each of the dataframes returned for the different star mass types
        for galaxy, cluster, target in zip(df['host_galaxy_name'], df['host_cluster_name'], df['target_name_ullyses']):
            # get the ULLYSES hlsp name to properly map]
            if target == 'Sextans-A':
                # there is an alias for a star (SEXTANS-A-LGN-S029) named 'SEXTANS-A'
                hlsp_targ = 'SEXTANS-A'
            else:
                hlsp_targ = match_aliases(target)
            if galaxy == 'MW':
                # use the cluster as the region name instead (low mass stars)
                galaxy_dict[hlsp_targ] = cluster
            else:
                if target == 'NGC3109':
                    # manually add in these because they had to be separated in the HLSPs
                    galaxy_dict['NGC3109-01'] = galaxy
                    galaxy_dict['NGC3109-02'] = galaxy
                else:
                    # high mass stars
                    galaxy_dict[hlsp_targ] = galaxy

    return galaxy_dict

#-------------------------------------------------------------------------------

def populate_kw_info(info, header, kw_dict):
    '''Use the header to fill in the common exposure keywords. If a keyword
       does not exist for that exposure, fill the value with "N/A" instead.
     '''

    for df_name, kw in kw_dict.items():
        try:
            if kw == 'ROOTNAME':
                info[df_name].append(header[kw].lower())
            else:
                info[df_name].append(header[kw])
        except KeyError:
            # does not exist for this type of file
            info[df_name].append('N/A')

    ## add exposure start information in both MJD and ISOT formats
    try:
        # HST
        expstart = header['EXPSTART']
    except KeyError:
        # FUSE
        expstart = header['OBSSTART']

    info['obs_date_mjd'].append(expstart)
    info['obs_date_isot'].append(Time(expstart, format='mjd').isot)

    return info

#-------------------------------------------------------------------------------

def populate_target_info(info, targname, ins, galaxy_dict):
    '''This function uses the target name provided in the header to fill in
       the HLSP target name and what region/galaxy the star exists in. It does
       this by using the data/target_metadata/*db.csv files. If the target is
       not in a file yet, it fills in the column with "TBD" & prints a warning.
    '''

    # use the utils function to find the matching alias
    hlsp_targ = match_aliases(targname)

    # Do something special for our pre-imaging
    if ins == 'WFC3':
        if targname == 'SEXTANS-A':
            # there is an alias for a star named 'SEXTANS-A'
            hlsp_targ = 'SEXTANS-A'
        # Header targnames for NGC3109 images are different than adopted HLSP names
        elif targname == "NGC-3109-V01":
            hlsp_targ = "NGC3109-01"
        elif targname == "NGC-3109-V02":
            hlsp_targ = "NGC3109-02"

    info['target_name_hlsp'].append(hlsp_targ) # add the HLSP name to the db

    # add the star region to the db
    try:
        # galaxy_dict was previously created in this script to match the target
        #   to the region/galaxy based on the target_metadata db files.
        info['star_region'].append(galaxy_dict[hlsp_targ])
    except KeyError:
        # if the star isn't in the db files, print an error & fill with "TBD"
        ull_targ = match_aliases(targname, return_name="target_name_ullyses")
        print(f'{ull_targ} / {hlsp_targ} is not in a database file yet. Make sure it gets in there!')
        info['star_region'].append('TBD')

    return info, hlsp_targ

#-------------------------------------------------------------------------------

def check_timeseries_yaml(hlsp_targname, ins, grating):
    '''This function reads in the timeseries configuration files in the data
       directory to determine if a specific target & grating combination is made
       into a time series HLSP and/or a sub exposure time series HLSP. If no
       configuration file exists, then it is assumed neither a time series nor
       sub exposure timeseries HLSP is created. If a file does exist, then the
       configuration file is read to determine if the grating matches any of the
       gratings in the file. It is assumed that all files for that target with
       that grating are made into a time series product.
    '''

    # the format for the name of the files is fixed
    yaml_file = f'data/timeseries/{hlsp_targname.lower()}_{ins.lower()}.yaml'

    exp_tss = False
    sub_exp_tss = False

    if os.path.exists(yaml_file):
        # if the configuration yaml file exists for this target, read it in
        #   to determine if an exposure or subexposure timeseries is created
        data = read_config(yaml_file)

        # There are rows in the file indicating True/False for exposure & sub
        # exposure level time series.
        if data['exp_tss'] == True and grating.lower() in data['gratings']:
            exp_tss = True

        # sub exposure level time series
        if data['sub_exp_tss'] == True and grating.lower() in data['gratings']:
            sub_exp_tss = True

    # if the configuration file doesn't exist, no timeseries HLSPs are created
    return exp_tss, sub_exp_tss

#-------------------------------------------------------------------------------

def populate_coadd(info, exp_tss, rootname, ins, grating, coadd_list):
    '''This function fills in the "coadd" function as True/False which will be
       use to create coadd products. All COS & STIS is coadded unless the file
       is made into a timeseries instead. Certain files will still have a coadd
       spectrum. Those can be found in the file
       `data/calibration_metadata/ullyses_custom_coadd.csv`.
    '''

    # check if the file was made into a timeseries
    if exp_tss:
        # check the list of special products that get coadds
        if rootname in coadd_list:
            # if it is in the list, make a coadd AND a timeseries
            coadd = True
        else:
            # if it is not in that list, it won't be coadded
            coadd = False
    elif ins == 'WFC3':
        # WFC3 images should not be coadded
        coadd = False
    elif grating == 'MIRVIS':
        # there's a special case where we took one confirmation image
       coadd = False
    else:
        # Otherwise, it should be coadded; FUSE is fudged a bit to make a cspec
        coadd = True

    info['coadd'].append(coadd)

    return info

#-------------------------------------------------------------------------------

def check_custom_cal(hlsp_targ, grating, rootname, blaze_roots):
    '''This function checks the different types of custom calibration
       possibilities when creating HLSPs. Each option has a specific custom
       configuration file of sorts that exists in the data directory.
       - STIS: If a custom extraction is done, "STIS" is returned. The directory
         `stis_configs` is where these configuration files exist.
       - WAVE: If a custom wavelength shift is performed, "WAVE" is returned.
         The directory `cos_shifts` is where these configuration files exist.
       - FUSE: If a custom FUSE flux rescaling is performed, "FUSE" is returned.
         The directory `fuse` contains notebooks for these custom calibrations.
       - BLAZEFIX: If the STIS blaze fix should be performed on echelle data,
         this flag will be set. There are no echelle datasets that have STIS
         custom extraction, so there should be no overlap.
       There should be no instances of overlap between these four calibration
       options, so there is nothing currently built in to handle that. If no
       special calibration is performed, None is returned.
    '''

    # Create paths for the STIS, wavelength shift, or FUSE configuration files
    #   for a specific target/grating configuration
    # the STIS yaml files can have an "archival" on the end of the file, too
    stis_yaml = glob.glob(f'data/stis_configs/{hlsp_targ.lower()}_{grating.lower()}*.yaml')
    wave_txt = f'data/cos_shifts/{hlsp_targ.lower()}_shifts.txt'
    # rootname is stripped of last "000" for the FUSE notebook names
    fuse_nb = f'data/fuse/{hlsp_targ.lower()}_{rootname[:-3]}.ipynb'

    if len(stis_yaml) > 0: # check for stis custom cal, first
        for syaml in stis_yaml:
            # there may be more than 1 yaml file for both archival & ullyses observed
            data = read_config(syaml)
            try:
                # read in the STIS configuration file and get the filename
                stis_roots = [data['infile'].split('_')[0]]
            except AttributeError:
                # this means that there's more than one data file in the yaml file
                # Instead, we need to get all of the rootnames as a list
                stis_roots = [s.split('_')[0] for s in data['infile'].keys()]

            # loop over all of the rootnames in the config file to find a match
            for stis_root in stis_roots:
                if stis_root == rootname:
                    # return a custom calibration of 'STIS' if the rootname matches
                    return 'STIS'


    # a separate "if" b/c there could be a stis_yaml file that matches for a
    #   COS rootname still because it is based on target and grating (e.g. G140L)
    if os.path.exists(wave_txt): # check for the COS wavelength shifts next
        wave_df = pd.read_csv(wave_txt,
                              names=['root', 'col2', 'col3', 'segment', 'shift'],
                              delim_whitespace=' ')

        # loop through each of the rootnames to find a match
        if rootname in list(wave_df['root']):
            return 'WAVE'

    elif os.path.exists(fuse_nb):
        # the FUSE targets that are custom calibrated will have a delivered notebook
        return 'FUSE'

    elif rootname in blaze_roots:
        # check to see if the rootname has the STIS blaze fix applied to it
        return 'BLAZEFIX'

    else:
        # otherwise, no special calibration is performed for this exposure
        return None

#-------------------------------------------------------------------------------

def check_quality_comm(qual_df, rootname):
    '''This function checks to see if a special quality comment should be added
       to the header of a file. These comments are specified in a csv file in
       the data directory: `data/calibration_metadata/ullyses_quality_comments.csv`.
       If there is no quality comment, a blank string is returned.
    '''

    # check to see if the rootname is in the quality comment file
    qual_comm = qual_df['qual_comm'][qual_df['dataset_name'] == rootname]

    if len(qual_comm) >= 1:
        # for a sanity check, make sure that there is only one entry per rootname
        if len(qual_comm) > 1:
            # if there is more than one, combine the comments
            # b/c each comment starts with the rootname, strip that off and add
            #   it only at the end instead.
            combined_qual = ' & '.join([' '.join(qual.split(' ')[1:]) for qual in qual_comm])
            print(f'Quality Comment: {rootname} repeated rootname; combining comments: {combined_qual}')
            return f"{qual_comm.iloc[0].split(' ')[0]} {combined_qual}"
        else:
            # if it is, return the comment
            return qual_comm.iloc[0]
    else:
        # otherwise, just return a blank string
        return ''

#-------------------------------------------------------------------------------

def populate_archival_status(info, ins, file_pid, ar_pids, ull_pids):
    '''This function uses the helper function `select_pids` to determine if
       the current rootname is part of the archival sample or the ULLYSES
       observations based on the program ID. If the PID is not incorperated in
       `select_pids`, then both fields will be populated with False.
    '''

    if ins == 'FUV':
        # FUSE data is all archival
        info['ullyses_obs'].append(False)
        info['archival_obs'].append(True)
    else:
        # search the proposal ids for if they are archival or ullyses observed
        if file_pid in ar_pids:
            info['ullyses_obs'].append(False)
            info['archival_obs'].append(True)
        elif file_pid in ull_pids:
            info['ullyses_obs'].append(True)
            info['archival_obs'].append(False)
        else:
            print(f"unrecognized PID! {file_pid}")
            info['ullyses_obs'].append(False)
            info['archival_obs'].append(False)

    return info

#-------------------------------------------------------------------------------

def populate_info(info, kw_dict, filename, galaxy_dict, ar_pids, ull_pids,
                  off_targs, coadd_list, qual_df, blaze_roots):
    '''This is the main function that fills in the database. It first checks
       it is not a calibration exposure (ACQ, WAVE, etc.). It then moves in to
       use the header to fill in exposure information. It then fills in the
       different target columns, the calibration flags, and the quality comments
       to be added in.
    '''

    with fits.open(filename) as hdu:
        # grab some useful header keywords that are used repeatedly
        targname = hdu[0].header['TARGNAME'] # to check for calibration exposures
        rootname = hdu[0].header['ROOTNAME'].lower() # lower to match helper files

        # skip this file if it is an ACQ or calibration exposure
        if (rootname.startswith('o') and 'ACQ' in hdu[0].header['OBSMODE']) or \
           (rootname.startswith('l') and 'ACQ' in hdu[0].header['EXPTYPE']):
            # we will get the ACQs if we glob on all raw files, exclude them
            return info
        elif "CCD" in targname or "WAVE" in targname or targname in off_targs:
            # we don't want to store the calibration files in this or offset targs
            # offset targets are in from data/target_metadata/ullyses_offset_targets.csv
            return info

        # grab even more keywords now that we're not looking at cal files
        ins = hdu[0].header['INSTRUME'] # to check if we're using WFC3 or FUSE
        if ins != 'FUV': # FUSE
            file_pid = str(hdu[0].header['PROPOSID']) # to check archival vs. ULLYSES
        else:
            # FUSE has a different keyword for this
            file_pid = str(hdu[0].header['PRGRM_ID'])

        try:
            grating = hdu[0].header['OPT_ELEM']
        except KeyError:
            # WFC3 & FUSE exposures won't have an OPT_ELEM keyword
            grating = ''

        ## fill in all of the easy header value keys
        info = populate_kw_info(info, hdu[0].header+hdu[1].header, kw_dict)

    ## target alias matching & filling in the galaxy/region
    info, hlsp_targ = populate_target_info(info, targname, ins, galaxy_dict)

    ## check if a part of the archival sample or the ULLYSES observations sample
    info = populate_archival_status(info, ins, file_pid, ar_pids, ull_pids)

    ## Check for the different calibration steps now
    # check the time series
    exp_tss, sub_exp_tss = check_timeseries_yaml(hlsp_targ, ins, grating)
    info['exp_timeseries'].append(exp_tss)
    info['subexp_timeseries'].append(sub_exp_tss)

    # check if the file should be made into a coadd file
    info = populate_coadd(info, exp_tss, rootname, ins, grating, coadd_list)

    # check the custom calibration column based on config files
    custom = check_custom_cal(hlsp_targ, grating, rootname, blaze_roots)
    info['custom_cal'].append(custom) # STIS, WAVE, FUSE, or None

    # check if there is anything special to add as a quality comment to the header
    qual_comm = check_quality_comm(qual_df, rootname)
    info['qual_comm'].append(qual_comm)

    # manually set the drizzle parameters to True for WFC3 images
    if ins == 'WFC3':
        info['drizzled'].append(True)
    else:
        # FUSE, COS, & STIS
        info['drizzled'].append(False)

    return info

#-------------------------------------------------------------------------------
def main(data_dir, save_dir='data', save_file='ullyses_calibration_db.csv'):
    '''Call the function to make the calibration database. Do a few things
       outside of the loop so that they don't have to be called 5000 times.
       This function assumes that the directory structure is such that there
       is a top level directory that contains the files in separate directories
       named with the ullyses_hlsp name.
    '''

    # These are the columns for the calibration database
    info = {'dataset_name' : [], # hdu[0].header['ROOTNAME']
            'observatory' : [], # hdu[0].header['TELESCOP']
            'instrument' : [], # hdu[0].header['INSTRUME']
            'proposid' : [], # hdu[0].header['PROPOSID']
            'detector' : [], # hdu[0].header['DETECTOR']
            'grating' : [], # hdu[0].header['OPT_ELEM']
            'filter' : [], ## hdu[0].header['FILTER']; WFC3 & STIS
            'cenwave' : [], # hdu[0].header['CENWAVE']
            'aperture' : [], # hdu[0].header['APERTURE']
            'lifetime_pos' : [], # hdu[0].header['LIFE_ADJ']
            'obs_date_mjd' : [], # hdu[1].header['EXPSTART']
            'obs_date_isot' : [], # time.date(hdu[1].header['EXPSTART'])
            'target_name' : [], # hdu[0].header['TARGNAME']
            'target_name_hlsp' : [], # match_aliases(hdu[0].header['TARGNAME'],
            'coadd' : [], # True/False If the products should be coadded
            'exp_timeseries' : [], # True/False does a timeseries yaml file exist for this target?
            'subexp_timeseries' : [], # True/False does the timeseries yaml file have a True for subexp?
            'drizzled' : [], # drizzled products are the WFC3 imaging only; True/False
            'custom_cal' : [], # STIS, WAVE, FUSE, or None
            'star_region' : [], # look for in the other CSVs
            'ullyses_obs' : [], # from a fixed list of ULLYSES PIDs
            'archival_obs' : [], # from a fixed list of archival PIDs
            'qual_comm' : [], # quality comment about the data from a fixed list
            }

    # mapping the column name with the associated keyword in the file header
    kw_dict = {'dataset_name' : 'ROOTNAME',
               'observatory' : 'TELESCOP',
               'instrument' : 'INSTRUME',
               'proposid' : 'PROPOSID',
               'detector' : 'DETECTOR',
               'grating' : 'OPT_ELEM',
               'filter' : 'FILTER',
               'cenwave' : 'CENWAVE',
               'aperture' : 'APERTURE',
               'lifetime_pos' : 'LIFE_ADJ',
               'target_name' : 'TARGNAME',
               }

    ## find all of the pids for archival & ULLYSES observed data
    # the keys of this dictionary are "ARCHIVAL" and "ULLYSES"
    pids_dict = select_all_pids(single_list=False)

    ## associate target names with regions
    galaxy_dict = make_galaxy_dict()

    ## offset targets
    offset_df = pd.read_csv('data/target_metadata/ullyses_offset_targets.csv')
    offset_targs = list(offset_df['offset_targ'])

    ## read in the rejected datasets and do not include in the final df
    rejected_df = pd.read_csv('data/calibration_metadata/ullyses_rejected_data.csv')
    rejected_roots = list(rejected_df['dataset_name'])

    ## read in the custom coadd datasets
    coadd_df = pd.read_csv('data/calibration_metadata/ullyses_custom_coadd.csv')
    coadd_list = list(coadd_df['dataset_name'])

    ## read in the quality comments to add to the database for certain datasets
    # we need both the quality comment and the rootname from this dataframe
    qual_df = pd.read_csv('data/calibration_metadata/ullyses_quality_comments.csv')

    ## read in the rootnames that should be used for applying the STIS blaze fix
    sbf_df = pd.read_csv('data/calibration_metadata/ullyses_stisblazefix.csv')
    blaze_roots = list(sbf_df['dataset_name'])

    ## fill in the dictionary for each file
    for targ_dir in np.sort(glob.glob(os.path.join(data_dir, '*'))):
        print(targ_dir)

        # grab the raw (COS, STIS, WFC3) & NVO (FUSE) files
        for rawf in np.sort(glob.glob(os.path.join(targ_dir, '*raw*.fits'))+ \
                            glob.glob(os.path.join(targ_dir, '*_vo.fits'))):

            # get the rootname, stripped of any additional text
            root = os.path.basename(rawf).split('_')[0].split('nvo')[0].lower()

            # skip the file if the rootname has already been recorded
            #   (COS will have two raw files)
            if root in info['dataset_name']:
                continue

            # after checking the file isn't in the db already, fix the rootname
            if len(root) == 11:
                # FUSE roots are weird. They have the extra 0s in the rejected roots file
                root = root + '00'

            # skip the file if it's been deiced it should not be in the sample
            if root in rejected_roots:
                continue

            # otherwise, fill in all of the columns!
            info = populate_info(info, kw_dict, rawf, galaxy_dict,
                                 pids_dict['ARCHIVAL'], pids_dict['ULLYSES'],
                                 offset_targs, coadd_list, qual_df, blaze_roots)

    ## save out the information
    internal_df = pd.DataFrame.from_dict(info)
    internal_df.to_csv(os.path.join(save_dir, save_file), index=False)
    print(f'Saved: {os.path.join(save_dir, save_file)}')
    print(internal_df)

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--indir", type=str, default=".",
                        help="Top level directory to search for files")
    parser.add_argument("-o", "--outdir", type=str, default='data/calibration_metadata',
                        help="Directory to save the outputs. \
                              The default behavior is to save to the \
                              data/calibration_metadata directory")
    parser.add_argument("-f", "--outfile", type=str, default='ullyses_calibration_db.csv',
                        help="Output filename. The default name is ullyses_calibration_db.csv")
    args = parser.parse_args()

    if not os.path.exists(args.indir):
        raise ValueError(f'{args.indir} does not exist. Please provide a valid input pathname.')

    if not os.path.exists(args.outdir):
        print(f'Making directory: {args.outdir}')
        os.mkdir(args.outdir)

    main(args.indir, save_dir=args.outdir, save_file=args.outfile)
