import numpy as np
import pandas as pd
import re

from ullyses_jira.parse_csv import parse_name_csv

def parse_inputs():
    # First, define all input files and parse them correctly
    juliafile = "/astro/ullyses/ARCHIVAL_DATA_HIGH_MASS/alias_file.csv"
    aliases = pd.read_csv(juliafile, comment="#") 
    # Remove leading or trailing spaces from both data and column names
    aliases = aliases.applymap(lambda x: x.strip() if isinstance(x, str) else x)  
    aliases.columns = aliases.columns.str.strip() 
    # All data should have a simbad_name entry, even if it is nan
    aliases["simbad_name"] = np.nan
    # Add missing TTS if not present 
    mask = aliases.apply(lambda row: row.astype(str).str.fullmatch(re.escape("TX-ORI")).any(), axis=1)
    if set(mask) == {False}:
        aliasescols = aliases.columns.values
        aliases.loc[len(aliases)] = ["TX-ORI", "V-TX-ORI"] + [np.nan for i in range(len(aliasescols)-2)]
    
    # Now read the preferred names files from the tech repo
    smc = parse_name_csv("smc", returndf=True)
    lmc = parse_name_csv("lmc", returndf=True)
    # The LMC file has a weird column that should be deleted
    lmc.drop(["Unnamed: 6"], axis=1, inplace=True)
    tts = parse_name_csv("tts", returndf=True)
    
    # Rename the columns to match columns in Julia's alias file. One map for Mag. clouds, one for TTS
    mcmap = {"Alternate_APT": "ULL_MAST_name", "APT": "ULL_name", "Alternate_PREFERRED": "alias0", "PREFERRED": "alias1", "SIMBAD_SEARCH_NAME": "simbad_name", "ORIGINAL": "alias3"}
    ttmap = {"Alternate_APT": "ULL_MAST_name", "PREFERRED": "alias0"} 
    lmc.rename(columns=mcmap, inplace=True)
    smc.rename(columns=mcmap, inplace=True) 
    tts.rename(columns=ttmap, inplace=True) 
    # What is this for...?
    tts["ULL_name"] = tts["ULL_MAST_name"]
    return  aliases, lmc, smc, tts


# Compare two dataframes, and if there is any overlap in any entries, combine
# all possible aliases for the matching target. If no overlap is found, add a
# new row for target and all its aliases
def add_aliases(comparison, all_aliases):
    comparisoninds = []
	for i in range(len(comparison)):
        already_present = False 
	    for col in comparison.columns: 
	        targ = comparison.iloc[i][col] 
	        # See if there is any overlap
            mask = all_aliases.apply(lambda row: row.astype(str).str.fullmatch(re.escape(targ)).any(), axis=1) 
            # If there is overlap, see if there are any comparison aliases to append
            if set(mask) != {False}: 
	            existing = all_aliases[mask].values[0] 
	            rowupdate = comparison.iloc[i] 
	            toadd = list(set(rowupdate) - set(existing))
				if len(toadd) == 0: # there are no comparison aliases
					break

                print(f"{len(toadd)} aliases to add to {all_aliases[mask]['ULL_MAST_name']}")
                # There could be empty columns to add comparison aliases into. If there
                # are not, add comparison columns with appropriate names
                emptycols = all_aliases.columns[all_aliases[mask].isna().any()].tolist()
	            if len(toadd) > len(emptycols): 
	                for comparisoncol in range(len(toadd)-len(emptycols)): 
	                    aliasno = len(all_aliases.columns)-2 
	                    all_aliases[f"alias{aliasno}"] = np.nan 
	                emptycols = all_aliases.columns[all_aliases[mask].isna().any()].tolist() 
	            
                for i in range(len(toadd)): 
	                all_aliases.loc[mask,emptycols[i]] = toadd[i] 
                already_present = True
                # Add the simbad name if it exists for a given target and is
                # a valid value
                if "simbad_name" in comparison.columns and comparison.iloc[i]["simbad_name"] != "NOT AVAILABLE IN SIMBAD":
                    all_aliases.loc[mask, "simbad_name"] = comparison.iloc[i]["simbad_name"]
	            break
        # If no overlap was found, add a comparison row with all aliases
        if already_present == False:
            print("Added a comparison row")
            rowupdate = comparison.iloc[i]
            all_aliasescols = all_aliases.columns.values
            missing = set(all_aliasescols) - set(rowupdate.index.values)
            for item in missing:
                rowupdate[item] = np.nan
            all_aliases.loc[len(all_aliases)] = rowupdate
    return all_aliases

def main():
    aliases, lmc, smc, tts = parse_inputs()
    for targetlist in [smc, lmc, tts]:
        aliases = add_aliases(targetlist, aliases)
    aliases.to_json("pd_all_aliases.json", orient="split")  

#################
#master_list = pd.read_pickle("pd_targetinfo.pkl") 
#new_ull = [] 
#new_alias = [] 
#for i in range(len(master_list)): 
#    simbad = master_list.iloc[i]["simbad_targname"] 
#    mast = master_list.iloc[i]["mast_targname"] 
#    print(simbad, mast) 
#    print(type(simbad), type(mast)) 
#    if not isinstance(simbad, str): 
#        simbad = "" 
#    if not isinstance(mast, str): 
#        mast = "" 
#    mask1 = aliases.apply(lambda row: row.astype(str).str.contains(simbad).any(), axis=1) 
#    if set(mask1) == {False}: 
#        mask2 = aliases.apply(lambda row: row.astype(str).str.contains(mast).any(), axis=1
#)  
#        if set(mask2) == {False}: 
#            new_ull.append(mast) 
#            new_alias.append(simbad) 
#
#new = pd.DataFrame({"ULL_name": new_ull, "alias0": new_alias})
#comb = pd.concat([aliases, new])
#comb.to_json("pd_all_aliases.json", orient="split")


