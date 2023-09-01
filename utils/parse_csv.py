from astropy.table import Table
import pandas as pd
import os
import numpy as np

dirname = os.path.dirname(__file__)

name_csvs = {"lmc": "LMC_Preferred_Names.csv",
             "smc": "SMC_Preferred_Names.csv",
             "tts": "lowmass_preferred_names.csv",
             "lowz": "lowz_preferred_names.csv"}
target_csvs = {"lmc":  ["LMC_sample_for_website_clean_newcoord_all_columns_order.csv"],
               "smc" : ["SMC_sample_for_website_clean_newcoord_and_names_all_columns.csv"],
               "lowz": ["low-metallicity-galaxy-targets.csv"],
               "ctts": ["classical-t-tauri-star-monitoring-targets.csv"],
               "tts" : ["Cha I_sample_for_website.csv", "CrA_sample_for_website.csv", "Lupus_sample_for_website.csv", "Ori OB1_sample_for_website.csv", "Sigma Ori_sample_for_website.csv", "eps Cha_sample_for_website.csv", "eta Cha_sample_for_website.csv", "Taurus_sample_for_website.csv", "TWA_sample_for_website.csv", "Lower Centaurus_sample_for_website.csv", "Upper Sco_sample_for_website.csv", "other_sample_for_website.csv"],
               "all": []}
database_csvs = {"lmc":  ["all_massive_star_metadata.csv"],
                 "smc" : ["all_massive_star_metadata.csv"],
                 "lowz": ["all_massive_star_metadata.csv", "lowz_db_metadata.csv"],
                 "ctts": ["full_sample_CTTS_for_DB.csv"],
                 "tts" : ["full_sample_CTTS_for_DB.csv"],
                 "all": []}

def parse_name_csv(target_type, returndf=False):
    target_type = target_type.lower()
    assert target_type in name_csvs, f"Target type {target_type} not recognized; acceptable values are 'lmc', 'smc', 'tts', or 'lowz'"
    csvfile = os.path.join(dirname, "data/target_metadata", name_csvs[target_type])
    if returndf == True:
        out = pd.read_csv(csvfile)
    else:
        out = change_names(csvfile)

    return out

def parse_target_csv(target_type):
    target_type = target_type.lower()
    assert target_type in target_csvs, "Target type not recognized; acceptable values are 'lmc', 'smc', 'lowz', 'ctts', 'tts', 'all'"
    dfs = []
    if target_type == "all":
        csvs = []
        for k in target_csvs:
            csvs += target_csvs[k]
    else:
        csvs = target_csvs[target_type]

    for csvfile0 in csvs:
        csvfile = os.path.join(dirname, "data/target_metadata", csvfile0)
        try:
            df = pd.read_csv(csvfile)
            # if 'metallicity' in csvfile:
            #     # Removing WFC3 rows
            #     remove_rows = df[(df['COS'] == 0) & (df['STIS'] == 0)]
            #     df = df.drop(df.index[remove_rows.index])
            #     print(f'Not including: {remove_rows}')
            dfs.append(df)
        except:
            print("ERROR! Could not read file, skipping {}".format(csvfile))
            csvs.pop(csvs.index(csvfile0))
            continue

    return csvs, dfs

def parse_database_csv(target_type):

    # using the dictionary defined above to map a galaxy/stellar region to the CSV file that contains info about it
    #   in the database era there are only 2 csv files now; 1 for high mass and 1 for low mass
    target_type = target_type.lower()
    assert target_type in database_csvs, "Target type not recognized; acceptable values are 'lmc', 'smc', 'lowz', 'ctts', 'tts', 'all'"

    # select the individual target file, or the combined target files
    if target_type == "all":
        csvs = list(np.unique(np.concatenate([tcsv for ttype, tcsv in database_csvs.items()])))
    else:
        csvs = database_csvs[target_type]

    dfs = []
    for csvfile0 in csvs:
        csvfile = os.path.join(dirname, "data/target_metadata", csvfile0)
        try:
            df = pd.read_csv(csvfile)
            dfs.append(df)
        except:
            print("ERROR! Could not read file, skipping {}".format(csvfile))
            csvs.pop(csvs.index(csvfile0))
            continue

    return csvs, dfs

def parse_aliases():
    aliasfile = os.path.join(dirname, "data/target_metadata", "ullyses_aliases.json")
    aliases = pd.read_csv(alias_file)
    return aliases

def change_names(name_change_file):
    '''
    WRITTEN BY RACHEL PLESHA: https://github.com/spacetelescope/ullyses_tech/blob/master/jira_connection/mass_issue_creation.py#L200
       The final files that were given in the website are different than those
       in the APT files. Since the box_to_jira.py script assumes that the names
       are the same, we need to change the names on the JIRA tickets to match.
       name_change_file : str
          The name of the file that contains a column 'Alternate_PREFERRED',
          which matches what is on the website, and 'Alternate_APT' which matches
          what is in the APT files.
    '''

    t = Table.read(name_change_file)
    names_dict = {}
    for website_name, apt_name in zip(t['PREFERRED'], t['Alternate_APT']):
        if website_name not in names_dict.keys():
            names_dict[website_name.strip()] = apt_name.strip()
        else:
            print(f'{website_name} repeated; not including {apt_name}')

    return names_dict
