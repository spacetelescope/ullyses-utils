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

def check_timeseries_yaml(hlsp_targname):

    yaml_file = f'data/timeseries/{hlsp_targname.lower()}.yaml'
    if os.path.exists(yaml_file):
        data = read_config(yaml_file)
        # There are rows in the file indicating True/False for timeseries & sub exposure
        return data['exp_tss'], data['sub_exp_tss']
    else:
        return False, False

#-------------------------------------------------------------------------------

def check_custom_cal(hlsp_targ, grating, rootname):
    # check the different types of custom calibration possibilities, all of
    #   which have some sort of custom calibration files in them

    ## STIS, WAVE, FUSE, or None
    stis_yaml = f'data/stis_configs/{hlsp_targ.lower()}_{grating.lower()}.yaml'
    wave_txt = f'data/cos_shifts/{hlsp_targ.lower()}_shifts.txt'
    fuse_nb = f'data/fuse/{hlsp_targ.lower()}_{rootname[:-3]}.ipynb' # rootname is stripped of last 000

    if os.path.exists(stis_yaml): # check for stis, first
        data = read_config(stis_yaml)
        try:
            stis_roots = [data['infile'].split('_')[0]]
        except AttributeError:
            # this means that there's more than one data file in the yaml file
            stis_roots = [s.split('_')[0] for s in data['infile'].keys()]
        for stis_root in stis_roots:
            if stis_root == rootname:
                # return a custom calibration of 'STIS' if the rootname matches
                return 'STIS'

    # this should be a separate if b/c there could be a stis_yaml file that matches
    #   for a COS rootname still
    if os.path.exists(wave_txt): # check for the COS wavelength shifts next
        wave_df = pd.read_csv(wave_txt,
                              names=['root', 'col2', 'col3', 'segment', 'shift'],
                              delim_whitespace=' ')
        if rootname in list(wave_df['root']):
            return 'WAVE'
    elif os.path.exists(fuse_nb):
        # the FUSE targets that are custom calibrated will have a delivered notebook
        return 'FUSE'
    else:
        return None

#-------------------------------------------------------------------------------

def check_quality_comm(qual_df, rootname):

    # check to see if the rootname is in the quality comment file
    qual_comm = qual_df['qual_comm'][qual_df['dataset_name'] == rootname]

    if len(qual_comm) >= 1:
        if len(qual_comm) > 1:
            print(f'{rootname} repeated rootname')
        # if it is, return the comment
        return qual_comm.iloc[0]
    else:
        # otherwise, just return a blank string
        return ''

#-------------------------------------------------------------------------------

def populate_info(info, kw_dict, filename, galaxy_dict, ar_pids, ull_pids,
                  off_targs, missing_metadata, coadd_list, qual_df):

    with fits.open(filename) as hdu:
        targname = hdu[0].header['TARGNAME']
        rootname = hdu[0].header['ROOTNAME'].lower()
        ins = hdu[0].header['INSTRUME']

        if (rootname.startswith('o') and 'ACQ' in hdu[0].header['OBSMODE']) or \
           (rootname.startswith('l') and 'ACQ' in hdu[0].header['EXPTYPE']):
            # we will get the ACQs if we glob on all raw files, exclude them
            return info, missing_metadata
        elif "CCD" in targname or "WAVE" in targname or targname in off_targs:
            # we don't want to store the calibration files in this or offset targs
            return info, missing_metadata

        ## fill in all of the easy header value keys
        for df_name, kw in kw_dict.items():
            try:
                if kw == 'ROOTNAME':
                    info[df_name].append(hdu[0].header[kw].lower())
                else:
                    info[df_name].append(hdu[0].header[kw])
            except KeyError:
                # does not exist for this type of file
                info[df_name].append('N/A')

        ## leftover values that need some sort of calculation

        # targname
        hlsp_targ = match_aliases(targname)
        if ins == 'WFC3' and targname == 'SEXTANS-A':
            # there is an alias for a star named 'SEXTANS-A'
            hlsp_targ = 'SEXTANS-A'

        info['target_name_hlsp'].append(hlsp_targ)
        try:
            info['star_region'].append(galaxy_dict[hlsp_targ])
        except KeyError:
            print(f'{match_aliases(targname, return_name="target_name_ullyses")} / {hlsp_targ} is not in a database file yet. Make sure it gets in there!')
            missing_metadata.append(hlsp_targ)
            info['star_region'].append('TBD')

        ## type of files
        exp_tss, sub_exp_tss = check_timeseries_yaml(hlsp_targ)
        info['exp_timeseries'].append(exp_tss) # does a timeseries yaml file exist for this target?
        info['subexp_timeseries'].append(sub_exp_tss) # might have to open the yaml file to see this one

        ## manually set the drizzle parameters to True for WFC3 images
        #  also grab some header info that is in a different place
        if ins == 'WFC3':
            info['drizzled'].append(True)
            expstart = hdu[0].header['EXPSTART'] # WFC3 has the expstart in thet primary extension
            grating = '' # no grating for WFC3
        elif ins == 'FUV': # FUSE
            info['drizzled'].append(False)
            expstart = hdu[0].header['OBSSTART']
            grating = '' # not something to select on FUSE
        else:
            # COS & STIS
            info['drizzled'].append(False)
            expstart = hdu[1].header['EXPSTART']
            grating = hdu[0].header['OPT_ELEM']

        # indication of if the file is coadded or not. All COS & STIS is coadded
        #   unless the file is made into a timeseries instead. Certain files
        #   will still have a coadd spectrum, however.
        if exp_tss:
            # check the list of special products that get coadds
            if rootname in coadd_list:
                coadd = True
            else:
                # if it is not in that list, it won't be coadded
                coadd = False
        elif ins == 'FUV': # FUSE
            coadd = False
        elif grating == 'MIRVIS':
            # there's a special case where we took one confirmation image
           coadd = False
        else:
            # Otherwise, it should be coadded
            coadd = True
        info['coadd'].append(coadd)

        ## time
        info['obs_date_mjd'].append(expstart)
        info['obs_date_isot'].append(Time(expstart, format='mjd').isot)

        ## populate the custom calibration column based on files already
        #    existing in the data directory of the repo
        custom = check_custom_cal(hlsp_targ, grating, rootname)
        info['custom_cal'].append(custom) # STIS, WAVE, FUSE, or None

        # check if there is anything special to add as a quality comment to the header
        qual_comm = check_quality_comm(qual_df, rootname)
        info['qual_comm'].append(qual_comm)

        ## Info unique to ULLYSES project
        if ins == 'FUV':
            # FUSE data is all archival
            info['ullyses_obs'].append(False)
            info['archival_obs'].append(True)
        else:
            # search the proposal ids for if they are archival or ullyses observed
            file_pid = str(hdu[0].header['PROPOSID'])
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

    return info, missing_metadata

#-------------------------------------------------------------------------------
def main(data_dir):

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
            'coadd' : [],
            'exp_timeseries' : [], # does a timeseries yaml file exist for this target?
            'subexp_timeseries' : [], # might have to open the yaml file to see this one
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
    pids_dict = select_all_pids(single_list=False)

    ## associate target names with regions
    csvs, csv_dfs = parse_database_csv(target_type='all')
    galaxy_dict = {}
    for df in csv_dfs:
        # loop through each of the dataframes returned for the different star mass types
        for galaxy, cluster, target in zip(df['host_galaxy_name'], df['host_cluster_name'], df['target_name_ullyses']):
            # get the ULLYSES hlsp name to properly map]
            if target == 'Sextans-A':
                # there is an alias for a star named 'SEXTANS-A'
                hlsp_targ = 'SEXTANS-A'
            else:
                hlsp_targ = match_aliases(target)
            if galaxy == 'MW':
                # use the cluster as the region name instead (low mass stars)
                galaxy_dict[hlsp_targ] = cluster
            else:
                if target == 'NGC3109':
                    # manually add in these because they had to be separated in the HLSPs
                    galaxy_dict['NGC-3109-V01'] = galaxy
                    galaxy_dict['NGC-3109-V02'] = galaxy
                else:
                    # high mass stars
                    galaxy_dict[hlsp_targ] = galaxy

    ## offset targets
    offset_df = pd.read_csv('data/target_metadata/ullyses_offset_targets.csv')

    ## read in the rejected datasets and do not include in the final df
    rejected_df = pd.read_csv('data/ullyses_rejected_data.csv')
    rejected_roots = list(rejected_df['dataset_name'])

    ## read in the custom coadd datasets
    coadd_df = pd.read_csv('data/custom_coadd.csv')
    coadd_list = list(coadd_df['dataset_name'])

    ## read in the quality comments to add to the database for certain datasets
    qual_df = pd.read_csv('data/ullyses_quality_comments.csv')

    skipped = []
    missing_meta = []
    ## fill in the dictionary for each file
    for targ_dir in np.sort(glob.glob(os.path.join(data_dir, '*'))):
        print(targ_dir)
        for rawf in np.sort(glob.glob(os.path.join(targ_dir, '*raw*.fits'))+ glob.glob(os.path.join(targ_dir, '*_vo.fits'))):
            root = os.path.basename(rawf).split('_')[0].split('nvo')[0].lower()

            # skip the file if the rootname has already been recorded
            #   (COS will have two raw files)
            if root in info['dataset_name']:
                continue

            if len(root) == 11:
                # FUSE roots are weird. They have the extra 0s in the rejected roots file
                root = root + '00'

            # skip the file if it's been deiced it should not be in the sample
            if root in rejected_roots:
                skipped.append(os.path.basename(rawf).split('_')[0].lower())
                continue
            # otherwise, fill in all of the columns!
            info, missing_meta = populate_info(info, kw_dict, rawf, galaxy_dict,
                                               pids_dict['ARCHIVAL'], pids_dict['ULLYSES'],
                                               np.array(offset_df['offset_targ']),
                                               missing_meta, coadd_list, qual_df)

    print('# Skipped b/c rejected:', len(np.unique(skipped)))
    for missing in np.unique(missing_meta):
        print(f'{match_aliases(missing, return_name="target_name_ullyses")} / {missing} is not in a database file yet. Make sure it gets in there!')

    ## save out the information
    internal_df = pd.DataFrame.from_dict(info)
    internal_df.to_csv('data/ullyses_calibration_db.csv', index=False)
    print(internal_df)

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    top_level_dir = "/astro/ullyses/ALL_DATA/"
    main(top_level_dir)
