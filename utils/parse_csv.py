import pandas as pd
import os
dirname = os.path.dirname(__file__)

from ullyses_jira.mass_issue_creation import change_names

name_csvs = {"lmc": "LMC_Preferred_Names.csv", 
             "smc": "SMC_Preferred_Names.csv",
             "tts": "lowmass_preferred_names.csv"}
target_csvs = {"lmc":  ["LMC_sample_for_website_clean_newcoord_all_columns_order.csv"],
               "smc" : ["SMC_sample_for_website_clean_newcoord_and_names_all_columns.csv"],
               "lowz": ["low-metallicity-galaxy-targets.csv"],
               "ctts": ["classical-t-tauri-star-monitoring-targets.csv"],
               "tts" : ["Cha I_sample_for_website.csv", "CrA_sample_for_website.csv", "Lupus_sample_for_website.csv", "Ori OB1_sample_for_website.csv", "Sigma Ori_sample_for_website.csv", "TWA_sample_for_website.csv", "eps Cha_sample_for_website.csv", "eta Cha_sample_for_website.csv"],
               "all": []}

def parse_name_csv(target_type):
    target_type = target_type.lower()
    assert target_type in name_csvs, "Target type not recognized; acceptable values are 'lmc', 'smc', or 'tts'"
    csvfile = os.path.join(dirname, "inputs", name_csvs[target_type])
    names_dict = change_names(csvfile)

    return names_dict

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
        csvfile = os.path.join(dirname, "inputs", csvfile0)
        try:
            df = pd.read_csv(csvfile)
            dfs.append(df)
        except:
            print("ERROR! Could not read file, skipping {}".format(csvfile))
            csvs.pop(csvs.index(csvfile0))
            continue

    return csvs, dfs

def parse_aliases():
    jsonfile = os.path.join(dirname, "inputs", "pd_all_aliases.json")
    aliases = pd.read_json(jsonfile, orient="split")
    return aliases
