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

def check_yaml(ull_targname):

    yaml_file = f'data/timeseries/{ull_targname.lower()}.yaml'
    if os.path.exists(yaml_file):
        data = read_config(yaml_file)
        return data['exp_tss'], data['sub_exp_tss']
    else:
        return False, False

#-------------------------------------------------------------------------------

def fill_in(info, kw_dict, filename, galaxy_dict, ar_pids, ull_pids, off_targs):

    with fits.open(filename) as hdu:
        targname = hdu[0].header["TARGNAME"]

        if 'ACQ' in hdu[0].header['OBSMODE']:
            # we will get the ACQs if we glob on all raw files
            return info
        elif "CCD" in targname or "WAVE" in targname or targname in off_targs:
            # we don't want to store the calibration files in this or offset targs
            return info

        ## fill in all of the easy header value keys
        for df_name, kw in kw_dict.items():
            try:
                info[df_name].append(hdu[0].header[kw])
            except KeyError:
                # does not exist for this type of file
                info[df_name].append('N/A')

        ## leftover values that need some sort of calculation
        # time
        info['obs_date_mjd'].append(hdu[1].header['EXPSTART'])
        info['obs_date_isot'].append(Time(hdu[1].header['EXPSTART'], format='mjd').isot)

        # targname
        ull_targ = match_aliases(targname)
        info['hlsp_targname'].append(ull_targ)
        try:
            info['star_region'].append(galaxy_dict[ull_targ])
        except KeyError:
            print(f'{ull_targ} is not in a database file yet. Make sure it gets in there!')
            info['star_region'].append('TBD')

        # type of files
        #info['coadd'].append(" ")
        exp_tss, sub_exp_tss = check_yaml(ull_targ)
        info['exp_timeseries'].append(exp_tss) # does a timeseries yaml file exist for this target?
        info['subexp_timeseries'].append(sub_exp_tss) # might have to open the yaml file to see this one
        #info['level0'].append() # I forget what we wanted with this column

        # data manipulation
        #info['drizzled'].append()
        #info['custom_cal'].append("") # TBD

        # Info unique to ULLYSES project
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

    return info

#-------------------------------------------------------------------------------
def main(data_dir):

    info = {'dataset_name' : [], # hdu[0].header['ROOTNAME']
            'observatory' : [], # hdu[0].header['TELESCOP']
            'instrument' : [], # hdu[0].header['INSTRUME']
            'proposid' : [], # hdu[0].header['PROPOSID']
            'detector' : [], # hdu[0].header['DETECTOR']
            'grating' : [], # hdu[0].header['OPT_ELEM']
            'filter' : [], ##
            'cenwave' : [], # hdu[0].header['CENWAVE']
            'aperture' : [], # hdu[0].header['APERTURE']
            'lifetime_pos' : [], # hdu[0].header['LIFE_ADJ']
            'obs_date_mjd' : [], # hdu[1].header['EXPSTART']
            'obs_date_isot' : [], # time.date(hdu[1].header['EXPSTART'])
            'obs_targname' : [], # hdu[0].header['TARGNAME']
            'hlsp_targname' : [], # match_aliases(hdu[0].header['TARGNAME'],
            #'coadd' : [],
            'exp_timeseries' : [], # does a timeseries yaml file exist for this target?
            'subexp_timeseries' : [], # might have to open the yaml file to see this one
            #'level0' : [], # I forget what we wanted with this column
            #'drizzled' : [],
            #'custom_cal' : [], # TBD
            'star_region' : [], # look for in the other CSVs?
            'ullyses_obs' : [], # from a fixed list of ULLYSES PIDs
            'archival_obs' : [], # from a fixed list of archival PIDs
            }

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
               'obs_targname' : 'TARGNAME',
               }

    ## find all of the pids for archival & ULLYSES observed data
    pids_dict = select_all_pids(return_all=False)

    ## associate target names with regions
    csvs, csv_dfs = parse_database_csv(target_type='all')
    galaxy_dict = {}
    for df in csv_dfs:
        for galaxy, cluster, target in zip(df['host_galaxy_name'], df['host_cluster_name'], df['target_name_std']):
            ull_targ = match_aliases(target)
            if galaxy == 'MW':
                # use the cluster as the region name instead
                galaxy_dict[ull_targ] = cluster
            else:
                galaxy_dict[ull_targ] = galaxy

    ## offset targets
    offset_df = pd.read_csv('data/target_metadata/ullyses_offset_targets.csv')

    # fill in the dictionary for each file
    for targ_dir in np.sort(glob.glob(os.path.join(data_dir, '*'))):
        print(targ_dir)
        for f in np.sort(glob.glob(os.path.join(targ_dir, '*raw*.fits'))):
            info = fill_in(info, kw_dict, f, galaxy_dict, pids_dict['ARCHIVAL'],
                           pids_dict['ULLYSES'], np.array(offset_df['offset_targ']))

    internal_df = pd.DataFrame.from_dict(info)
    internal_df.to_csv('data/internal_database.csv', index=False)
    print(internal_df)

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    top_level_dir = "/astro/ullyses/ALL_DATA/"
    main(top_level_dir)
