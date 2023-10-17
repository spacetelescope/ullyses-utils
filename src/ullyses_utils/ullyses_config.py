VERSION = "dr6"
CAL_VER = "2.1.2"

# Some targets have periods in their name and these can break MAST ingest
# Rename them to remove periods and strip any trailing numbers after periods
RENAME = {
          "echa-j0843.3-7915": "echa-j0843-7915",
          "echa-j0844.2-7833": "echa-j0844-7833",
          "moa-j010321.3-720538": "moa-j010321-720538",
          "ogle-j004942.75-731717.7": "ogle-j004942-731717",
          "pgz2001-j161031.9-191305": "pgz2001-j161031-191305",
          "pz99-j161019.1-250230": "pz99-j161019-250230",
          "rxj0438.6+1546": "rxj0438+1546",
          "rxj1852.3-3700": "rxj1852-3700",
          "rxj1556.1-3655": "rxj1556-3655",
          "rxj1842.9-3532": "rxj1842-3532",
          "sstc2dj160000.6-422158": "sstc2dj160000-422158",
          "sstc2dj160830.7-382827": "sstc2dj160830-382827",
          "sstc2dj161243.8-381503": "sstc2dj161243-381503",
          "sstc2dj161344.1-373646": "sstc2dj161344-373646",
          "sstc2dj161243.8-381503": "sstc2dj161243-381503"
          }

