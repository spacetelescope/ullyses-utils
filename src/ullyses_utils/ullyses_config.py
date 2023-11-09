VERSION = "dr6"
CAL_VER = "3.0"

# Some targets have periods in their name and these can break MAST ingest.
# Also, targets that have coordinates in their name should change the dec
# sign from - to m, and from + to p.
# Rename them to remove periods and strip any trailing numbers after periods
RENAME = {
          "2massj04383885+1546045": "2massj04383885p1546045",
          "2mass-j04390163+2336029": "2mass-j04390163p2336029",
          "2massj11432669-7804454": "2massj11432669m7804454",
          "2mass-j15570234-1950419": "2mass-j15570234m1950419",
          "echa-j0843.3-7915": "echa-j0843m7915",
          "echa-j0844.2-7833": "echa-j0844m7833",
          "moa-j010321.3-720538": "moa-j010321m720538",
          "ogle-j004942.75-731717.7": "ogle-j004942m731717",
          "pgz2001-j161031.9-191305": "pgz2001-j161031m191305",
          "pz99-j161019.1-250230": "pz99-j161019m250230",
          "rxj0438.6+1546": "rxj0438p1546",
          "rxj1852.3-3700": "rxj1852m3700",
          "rxj1556.1-3655": "rxj1556m3655",
          "rxj1608.9-3905": "rxj1608m3905",
          "rxj1842.9-3532": "rxj1842m3532",
          "sstc2dj160000.6-422158": "sstc2dj160000m422158",
          "sstc2dj160830.7-382827": "sstc2dj160830m382827",
          "sstc2dj161243.8-381503": "sstc2dj161243m381503",
          "sstc2dj161344.1-373646": "sstc2dj161344m373646",
          "sstc2dj161243.8-381503": "sstc2dj161243m381503",
          }

