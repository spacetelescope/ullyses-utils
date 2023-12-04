import numpy as np

def select_all_pids(massive=False, tts=False, extra=True, monitoring=True, single_list=True):
    '''Use this function if you want to select more than one region's PIDs at once.
    The logic behind writing this is:
    1) if you want massive stars (LMC, SMC, lowz), specify massive=True. If you
    do not want the "extra" stars included in the ULLYSES sample (i.e. stars
    that were added after the original sample was created to fill the
    luminosity/class bins), then specify extra=False.
      -> Original sample + Extra sample: pids = select_all_pids(massive=True)
      -> Original sample only: pids = select_all_pids(massive=True, extra=False)
    2) if you want all regions of the t-tauri star sample, including the monitoring
    stars, specify tts=True. If you do not want the monitoring stars in the sample
    then specify monitoring=False.
      -> All TTS: pids = select_all_pids(tts=True)
      -> All TTS but the monitoring: pids = select_all_pids(tts=True, monitoring=False)
    3) You want the entire sample of everything.
      -> pids = select_all_pids()
    4) If you want some combination of massive stars without the extra sample
    *and* the TTS without the monitoring (or some combination), you can specify
    a combination of the above keywords. For example:
      -> pids = select_all_pids(massive=True, tts=True, extra=False)
    There is an additional keyword "single_list" that is set to True by default,
    which means you get a list of PIDs for both ULLYSES observed and archival
    datasets. If you would like those separated out, specify single_list=False,
    and the function will return a dictionary with the two lists separated out
    with the keys "ULLYSES" and "ARCHIVAL".

    Inputs
    -------
    massive : Boolean (default=False)
        Get massive stars (LMC, SMC, & Low-Z)
    tts : Boolean (default=False)
        Get all t-tauri stars
    extra : Boolean (default=True)
        should be used exclusively with "massive". Use to get the stars not
        originally included in the core ULLYSES sample.
    monitoring : Boolean (default=True)
        should be used exclusively with "tts". Use to get the monitoring stars.
    single_list : Boolean (default=True)
        By default, return both ULLYSES observed and archival samples together.
        If False, this will return a dictionary instead with the two lists of
        PIDs separated out under the keys "ULLYSES" and "ARCHIVAL"

    Outputs
    -------
    all_pids : list (single_list=True) or dict (single_list=False)
    '''

    all_regions = ["smc-extra", "smc", "lmc-extra", "lmc", "lowz-extra", "lowz-image",
                   "lowz", "monitoring_tts", "cha i", "cra", "eps cha", "eta cha",
                   "lambda orionis", "lupus", "ori ob", "sigma ori", "taurus", "twa",
                   "lower centaurus", "upper scorpius", "other"]


    ## establish which of the regions should be searched over based on inputs
    search_regions = []

    # grab everything (by default)
    if massive is False and tts is False and monitoring is True and extra is True:
        search_regions = all_regions
    else:
        # Massive stars?
        if massive is True:
            search_regions.extend(["smc", "lmc", "lowz-image", "lowz"])

            # Extra sample? (not originally included in ULLYSES core sample)
            if extra is True:
                search_regions.extend(["smc-extra", "lmc-extra", "lowz-extra"])

        # TTS?
        if tts is True:
            search_regions.extend(["cha i", "cra", "eps cha", "eta cha", "lambda orionis",
                                   "lupus", "ori ob", "sigma ori", "taurus", "twa",
                                   "lower centaurus", "upper scorpius", "other"])
            # Monitoring TTS?
            if monitoring is True:
                search_regions.extend(["monitoring_tts"])

    ## return ULLYSES vs. archival PIDs or combined PIDs (default)
    if single_list:
        all_pids = []
        for region in search_regions:
            all_pids.extend(select_pids(region))
        all_pids = list(np.unique(all_pids))
    else:
        ull_pids = []
        ar_pids = []
        for region in search_regions:
            ull, ar = select_pids(region, single_list=False)
            ull_pids.extend(ull)
            ar_pids.extend(ar)

        all_pids = {'ULLYSES' : list(np.unique(ull_pids)),
                    'ARCHIVAL' : list(np.unique(ar_pids))}

    return all_pids

#-------------------------------------------------------------------------------

def select_pids(selected_region, single_list=True):
    '''This function returns pids given a region. "Extra" regions are separated
    out as these include datasets that were not originally in the ULLYSES sample.
    The TTS regions are separated by their host cluster. Low metallicity stars
    are separated by imaging and spectroscopic observations.

    Inputs
    ------
    selected_region : str
        Accepted regions:
          - "smc-extra", "smc", "lmc-extra", "lmc",
            "lowz-extra", "lowz-image", "lowz",
            "monitoring_tts",
            "cha i", "cra", "eps cha", "eta cha", "lupus", "ori ob", "sigma ori",
              "taurus", "twa", "lower centaurus", "upper scorpius", "other", "lambda orionis"
    single_list : Boolean
      True by default. If true, a list of pids for the specified region is returned.
      If false, two lists of pids are returned; one is only the ULLYSES observed
      PIDs (those the team made Phase 2s for from 2020-2023), and then other is
      only the archival data used in the HLSP creation and delivered to MAST.

    Outputs
    -------
    if single_list = True --
        ull_pids + ar_pids : list
          combined ULLYSES observed PIDs and archival data. ULLYSES observed
          PIDs are first.
    if single_list == False --
        ull_pids : list
          ULLYSES observed PIDs (those the team made Phase 2s for from 2020-2023)
        ar_pids : list
          archival observed PIDs (used in the HLSP creation)
    '''

    if "smc-extra" in selected_region:
        ar_pids = ['7437', '9116', '9412', '11625', '12978', '13778', '15629',
                   '15837'] # archival
        ull_pids = [] # ULLYSES
    elif "smc" in selected_region:
        ar_pids = ['7437', '7480', '8145', '8566', '9094', '9116', '9383', '9434',
                   '11487', '11489', '11623', '11625', '11997', '12010', '12425',
                   '12581', '12717', '12805', '13004', '13122', '13373', '13522',
                   '13778', '13931', '13969', '14081', '14437', '14476', '14503',
                   '14712', '14855', '14909', '15366', '15385', '15536', '15629',
                   '15774', '15837', '16230'] # archival
        ull_pids = ['16098', '16099', '16100', '16101', '16102', '16103', '16368',
                    '16370', '16371', '16372', '16373', '16375', '16802', '16803',
                    '16805', '16806', '16807', '16808', '16809', '17295'] # ULLYSES
    elif "lmc-extra" in selected_region:
        ar_pids = ['7299', '9434', '11692', '12581', '13806', '13780', '13781',
                   '14081', '14246', '14675', '14683', '14712', '15629', '15824',
                   '16272', '17074', '17279'] # archival
        ull_pids = [] # ULLYSES
    elif "lmc" in selected_region:
        ar_pids = ['7299', '7392', '8320', '8662', '9434', '9757', '12218', '12581',
                   '12978', '14675', '14683', '15629', '15824', '16304', '16230'] # archival
        ull_pids = ['16090', '16091', '16092', '16093', '16094', '16095', '16096',
                    '16097', '16364', '16365', '16366', '16367', '16369', '16374',
                    '16810', '16811', '16812', '16813', '16814', '16815', '16816',
                    '16817', '16818', '16819', '16820', '16821', '16822', '16823',
                    '16824', '16825', '16826', '17296'] # ULLYSES
    elif "lowz-extra" in selected_region:
        ar_pids = ['8662', '12587', '12867', '14245', '15156', '15880', '15921',
                   '15967', '16647', '16717', '16767', '16920'] # archival
        ull_pids = [] # ULLYSES
    elif "lowz-image" in selected_region:
        ar_pids = [] # archival
        ull_pids = ['16104'] # ULLYSES
    elif "lowz" in selected_region:
        ar_pids = [] # archival
        ull_pids = ['16511', '16930'] # ULLYSES
    elif "monitoring_tts" in selected_region:
        ar_pids = ['8157', '9081', '9374', '11608', '11616', '12315', '13775',
                   '14048', '15204', '15165', '16010'] # archival
        ull_pids = ['16107', '16108', '16109', '16110', '16478', '16589',
                    '16590', '16591', '16592'] # ULLYSES
    elif selected_region == 'cha i':
        ar_pids = ['11616', '16478', '13775', '14193'] # archival
        ull_pids = ['16481', '16482', '16596', '16597', '16598'] # ULLYSES
    elif selected_region == 'cra':
        ar_pids = [] # archival
        ull_pids = ['16859'] # ULLYSES
    elif selected_region == 'eps cha':
        ar_pids = ['9241', '15128', '11616'] # archival
        ull_pids = ['16599'] # ULLYSES
    elif selected_region == 'eta cha':
        ar_pids = ['11616', '12876'] # archival
        ull_pids = ['16480', '16595', '16596'] # ULLYSES
    elif selected_region == 'lupus':
        ar_pids = ['8205', '9807', '11616', '12036', '13032', '14177', '14469',
                   '14604', '14703', '15070', '15210'] # archival
        ull_pids = ['16476', '16477', '16479', '16853', '16854',
                    '16855', '16856', '16857', '16858'] # ULLYSES
    elif selected_region == 'ori ob':
        ar_pids = ['8317', '12996', '13363', '15070'] # archival
        ull_pids = ['16113', '16114', '16115'] # ULLYSES
    elif selected_region == 'sigma ori':
        ar_pids = [] # archival
        ull_pids = ['16113', '16594'] # ULLYSES
    elif selected_region == 'taurus':
        ar_pids = ['7718', '8206', '8157', '8238', '8316', '8317', '8627', '9081',
                   '9093', '9374', '9435', '9785', '9790', '11533', '11608', '11616',
                   '11660', '12036', '12161', '12199', '12876', '12907', '13714',
                   '13766', '15070', '17176'] # archival
        ull_pids = ['16593'] # ULLYSES
    elif selected_region == 'twa':
        ar_pids = ['8041', '9093', '9841', '11608', '11531', '11616', '15204'] # archival
        ull_pids = [] # ULLYSES
    elif selected_region == 'lower centaurus':
        ar_pids = ['11616'] # archival
        ull_pids = [] # ULLYSES
    elif selected_region == 'upper scorpius':
        ar_pids = ['9790', '13372', '15310', '16290'] # archival
        ull_pids = [] # ULLYSES
    elif selected_region == 'lambda orionis':
        ar_pids = ['8317', '12996', '15070'] # archival
        ull_pids = [] # ULLYSES
    elif selected_region == 'other':
        ar_pids = ['7565', '8317', '8801', '11828', '12996', '13032', '14690'] # archival
        ull_pids = [] # ULLYSES
    else:
        print('Region not recognized:', selected_region)
        ar_pids = [] # archival
        ull_pids = [] # ULLYSES

    if single_list is True:
        return ull_pids + ar_pids
    else:
        return ull_pids, ar_pids
