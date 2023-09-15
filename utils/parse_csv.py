from astropy.table import Table
import pandas as pd
import os
import numpy as np

dirname = os.path.dirname(__file__)

database_csvs = {"lmc":  ["highmass_star_db_metadata.csv"],
                 "smc" : ["highmass_star_db_metadata.csv"],
                 "lowz": ["highmass_star_db_metadata.csv", "lowz_galaxy_db_metadata.csv"],
                 "ctts": ["lowmass_star_db_metadata.csv"],
                 "tts" : ["lowmass_star_db_metadata.csv"],
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
    alias_file = os.path.join(dirname, "data/target_metadata", "ullyses_aliases.csv")
    aliases = pd.read_csv(alias_file)
    return aliases
