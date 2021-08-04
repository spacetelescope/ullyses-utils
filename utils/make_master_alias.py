from collections import defaultdict
from astropy.io import fits
import glob
import os
import argparse
import numpy as np
import pandas as pd
import re

from ullyses_jira.parse_csv import parse_name_csv

JULIAFILE = "inputs/julia_alias_file.csv"
FUSEFILE1 = "inputs/fuse_aliases1.json"
FUSEFILE2 = "inputs/fuse_aliases2.json"


def parse_inputs():
    # First, define all input files and parse them correctly
    aliases = pd.read_csv(JULIAFILE, comment="#")
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
    lowz = parse_name_csv("lowz", returndf=True)

    # Rename the columns to match columns in Julia's alias file. One map for Mag. clouds, one for TTS
    mcmap = {"Alternate_APT": "ULL_MAST_name",
             "PREFERRED": "ULL_name",
             "Alternate_PREFERRED": "alias0",
             "APT": "alias1",
             "SIMBAD_SEARCH_NAME": "simbad_name",
             "ORIGINAL": "alias2"}
    ttmap = {"Alternate_APT": "ULL_MAST_name", "PREFERRED": "ULL_name"}
    lmc.rename(columns=mcmap, inplace=True)
    smc.rename(columns=mcmap, inplace=True)
    tts.rename(columns=ttmap, inplace=True)
    lowz.rename(columns=ttmap, inplace=True)
#    # What is this for...?
#    tts["ULL_name"] = tts["ULL_MAST_name"]
    aliases = clean_df(aliases)
    lmc = clean_df(lmc)
    smc = clean_df(smc)
    tts = clean_df(tts)
    lowz = clean_df(lowz)
    return  aliases, lmc, smc, tts, lowz


def clean_df(df):
    df = df.fillna('TEMPORARYNANISTEMPORARY').apply(lambda x :x.str.upper()).replace('TEMPORARYNANISTEMPORARY', np.nan)
    df = df.replace("NaN", np.nan)
    df = df.replace("NAN", np.nan)
    df = df.replace("nan", np.nan)
    return df


# Compare two dataframes, and if there is any overlap in any entries, combine
# all possible aliases for the matching target. If no overlap is found, add a
# new row for target and all its aliases
def add_aliases(comparison, all_aliases, verbose=False):
    """
    Row by row and column by column, combine two dataframes that both contain
    alias information. First try to match a target in a comparison df
    to a ever-growing all_aliases df. If there is a match and if any aliases
    from comparison are not in all_aliases, add them (adding more columns
    if necessary). If there is not a match, add the entire row from comparison
    to all_aliases.
    """
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
                    already_present = True
                    break

                if verbose is True:
                    print(f"{len(toadd)} aliases to add to {all_aliases[mask]['ULL_MAST_name']}")
                # There could be empty columns to add comparison aliases into. If there
                # are not, add new columns with appropriate names
                emptycols0 = all_aliases.columns[all_aliases[mask].isna().any()].tolist() # could include simbad_targname
                emptycols = [x for x in emptycols0 if x != "simbad_targname"]
                if len(toadd) > len(emptycols):
                    for comparisoncol in range(len(toadd)-len(emptycols)):
                        aliasno = len(all_aliases.columns)-2
                        all_aliases[f"alias{aliasno}"] = np.nan
                    emptycols = all_aliases.columns[all_aliases[mask].isna().any()].tolist()

                for j in range(len(toadd)):
                    all_aliases.loc[mask,emptycols[j]] = toadd[j]
                already_present = True
                # Add the simbad name if it exists for a given target and is
                # a valid value
                if "simbad_name" in comparison.columns and comparison.iloc[i]["simbad_name"] != "NOT AVAILABLE IN SIMBAD":
                    all_aliases.loc[mask, "simbad_name"] = comparison.iloc[i]["simbad_name"]
                break
        # If no overlap was found, add a comparison row with all aliases
        if already_present == False:
            if verbose is True:
                print("Added a new row")
            rowupdate = comparison.iloc[i]
            all_aliasescols = all_aliases.columns.values
            missing = set(all_aliasescols) - set(rowupdate.index.values)
            for item in missing:
                rowupdate[item] = np.nan
            all_aliases.loc[len(all_aliases)] = rowupdate
    return all_aliases


def fix_pipes(all_aliases):
    for i in range(len(all_aliases)):
        s = all_aliases.iloc[i]
        match = s.str.contains("|", regex=False, na=False)
        if True in match.values:
            a = s[match].values[0]
            targs = a.split("|")
            exists = []
            for j in range(len(targs)):
                tmatch = s.str.fullmatch(re.escape(targs[j])).any()
                if tmatch is True:
                    exists.append(targs[j])
            targs = [x for x in targs if x not in exists]
            empty = s.isna()
            emptycols0 = s[empty].index.values
            emptycols = [x for x in emptycols0 if x != "simbad_targname"]
            if len(emptycols) < len(targs):
                for new in range(2-len(emptycols)):
                    aliasno = len(all_aliases.columns)-2
                    all_aliases[f"alias{aliasno}"] = np.nan
                s = all_aliases.iloc[i]
                empty = s.isna()
                emptycols0 = s[empty].index.values
                emptycols = [x for x in emptycols0 if x != "simbad_targname"]
            for j in range(len(targs)):
                all_aliases.loc[i, emptycols[j]] = targs[j]

    return all_aliases

# NOT IN USE
def create_fuse_alias2():
# NOT IN USE
    fuse_targs0 = glob.glob("/astro/ullyses/ullyses_target/data/SMC/FUSE/*") + \
                  glob.glob("/astro/ullyses/ullyses_target/data/LMC/FUSE/*") + \
                  glob.glob("/astro/ullyses/ullyses_target/data/SMC_FUSE/FUSE/*") + \
                  glob.glob("/astro/ullyses/ullyses_target/data/LMC_FUSE/FUSE/*")
    fuse_targs = [os.path.basename(x) for x in fuse_targs0]
    fuse_targs_upper = [x.upper() for x in fuse_targs]

    fuse_dicts = []
    for i in range(len(fuse_targs0)):
        fuse_d = {}
        fuse_d["dirname"] = fuse_targs_upper[i]

        partial_d = fuse_targs0[i]
        partial_d = partial_d.replace("[", "LEFTBRACKET")
        partial_d = partial_d.replace("]", "RIGHTBRACKET")
        partial_d = partial_d.replace("LEFTBRACKET", "[[]")
        partial_d = partial_d.replace("RIGHTBRACKET", "[]]")
        files = glob.glob(os.path.join(partial_d, "*", "*.fit*"))
        targnames0 = [fits.getval(x, "targname") for x in files]
        targnames = list(set(targnames0))
        for j in range(len(targnames)):
            fuse_d[f"targname{j}"] = targnames[j]
        fuse_dicts.append(fuse_d)

    df = pd.DataFrame(fuse_dicts)
    df = clean_df(df)
    df.to_json("inputs/fuse_target_aliases.json", orient="split")
    print("Wrote inputs/fuse_target_aliases.json")


# manual_insert.json includes manually matched FUSE names to ULLYSES names.
# This only needs to be run once and never again.
def create_fuse_alias(infile="inputs/manual_insert.json"):
    fuse_targs0 = glob.glob("/astro/ullyses/ullyses_target/data/SMC/FUSE/*") + \
                  glob.glob("/astro/ullyses/ullyses_target/data/LMC/FUSE/*") + \
                  glob.glob("/astro/ullyses/ullyses_target/data/SMC_FUSE/FUSE/*") + \
                  glob.glob("/astro/ullyses/ullyses_target/data/LMC_FUSE/FUSE/*")
    fuse_targs = [os.path.basename(x) for x in fuse_targs0]
    fuse_targs_upper = [x.upper() for x in fuse_targs]

    df = pd.read_json(infile, orient="split")
    for i in range(len(df)):
        fuse_targ = df.loc[i, "alias0"]
        fuse_targ = fuse_targ.upper()

        inds = [j for j in range(len(fuse_targs_upper)) if fuse_targs_upper[j] == fuse_targ]
        toadd = []
        for ind in inds:
            d = fuse_targs0[ind]
            d = d.replace("[", "LEFTBRACKET")
            d = d.replace("]", "RIGHTBRACKET")
            d = d.replace("LEFTBRACKET", "[[]")
            d = d.replace("RIGHTBRACKET", "[]]")
            files = glob.glob(os.path.join(d, "*", "*.fit*"))
            toadd0 = [fits.getval(x, "targname") for x in files]
            toadd += list(set(toadd0))

        toadd = list(set(toadd))

        emptycols = df.columns[df.iloc[i].isna()].tolist()
        if len(toadd) > len(emptycols):
            for comparisoncol in range(len(toadd)-len(emptycols)):
                aliasno = len(df.columns)-1
                df[f"alias{aliasno}"] = np.nan
            emptycols = df.columns[df.iloc[i].isna()].tolist()
        for j in range(len(toadd)):
            df.loc[i,emptycols[j]] = toadd[j]



    df = clean_df(df)
    df.to_json(FUSEFILE1, orient="split")
    print(f"Wrote {FUSEFILE1}")


def main(verbose=False):
    aliases, lmc, smc, tts, lowz = parse_inputs()
    fuse_alias1 = pd.read_json(FUSEFILE1, orient="split")
    fuse_alias2 = pd.read_json(FUSEFILE2, orient="split")
    for targetlist in [smc, lmc, tts, lowz, fuse_alias1, fuse_alias2]:
        aliases = add_aliases(targetlist, aliases, verbose)
    aliases = fix_pipes(aliases)
    aliases = clean_df(aliases)
    aliases = aliases.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    aliases.to_json("inputs/pd_all_aliases.json", orient="split")
    aliases.to_csv("inputs/pd_all_aliases.csv")
    print("Wrote inputs/pd_all_aliases.json and pd_all_aliases.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", default=False,
                        action="store_true",
                        help="If True, print what aliases were found or added")
    args = parser.parse_args()
    main(args.verbose)
