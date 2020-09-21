import os
dirname = os.path.dirname(__file__)

from .mass_issue_creation import change_names

name_csvs = {"lmc": os.path.join(dirname, "inputs/LMC_Preferred_Names.csv"), 
             "smc": os.path.join(dirname, "inputs/SMC_Preferred_Names.csv"),
             "tts": os.path.join(dirname, "inputs/lowmass_preferred_names.csv")}

def parse_name_csv(target_type):
    target_type = target_type.lower()
    assert target_type in name_csvs, "Target type not recognized; acceptable values are 'lmc', 'smc', or 'tts'"
    csvfile = name_csvs[target_type]
    names_dict = change_names(csvfile)

    return names_dict

