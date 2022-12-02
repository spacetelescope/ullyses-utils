;;This is a wrapper that calls lcogt_uphot.pro 4 times, once for each
;;DR5 target with u-band data

;;The directory names are the MAST names. The second argument needs to
;;be a name recognizable by SIMBAD.

pro lcogt_dr5_u

  lcogt_uphot,'/astro/ullyses/lcogt_data/V-TW-HYA/','V* TW Hya'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-RU-LUP/','V* RU Lup'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-BP-TAU/','V* BP Tau'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-GM-AUR/','V* GM Aur'

end
