;;This wrapper calls lcogt_phot.pro once for each DR4 target.

;;The directory names are the MAST names. The second argument needs to
;;be a name recognizable by SIMBAD.

pro lcogt_dr4

  lcogt_phot,'/astro/ullyses/lcogt_data/2MASS-J11432669M7804454/','2MASS J11432669-7804454'
  lcogt_phot,'/astro/ullyses/lcogt_data/CHX-18N/','CHX 18N'
  lcogt_phot,'/astro/ullyses/lcogt_data/ECHA-J0844M7833/','ECHA J0844.2-7833'
  lcogt_phot,'/astro/ullyses/lcogt_data/HN-5/','Hn 5'
  lcogt_phot,'/astro/ullyses/lcogt_data/SSTC2D-J160000M422158/','SSTc2d J160000.6-422158'
  lcogt_phot,'/astro/ullyses/lcogt_data/SSTC2D-J161344M373646/','SSTc2d J161344.1-373646'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-10/','Sz 10'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-111/','Sz 111'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-130/','Sz 130'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-45/','Sz 45'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-66/','Sz 66'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-69/','Sz 69'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-71/','Sz 71'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-72/','Sz 72'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-75/','Sz 75'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-76/','Sz 76'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ-77/','Sz 77'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-IN-CHA/','V* IN Cha'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-TW-HYA/','V* TW Hya'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-XX-CHA/','V* XX Cha'

end
