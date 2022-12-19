;;This is a wrapper that calls lcogt_uphot.pro 3 times, once for each
;;DR6 target with u-band data

;;The directory names are the MAST names. The second argument needs to
;;be a name recognizable by SIMBAD.

pro lcogt_dr6_u

  lcogt_uphot,'/astro/ullyses/lcogt_data/V-TW-HYA/','V* TW Hya'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-RU-LUP/','V* RU Lup'
  lcogt_uphot,'/astro/ullyses/lcogt_data/SZ82/','Sz 82'

end
