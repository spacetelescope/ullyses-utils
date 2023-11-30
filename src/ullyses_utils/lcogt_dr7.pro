;;This wrapper calls lcogt_phot.pro once for each DR7 target.
;;It also calls lcogt_uphot.pro once for each DR7 target with u-band data.
;;Then it runs a script that combines the Vi and u output.

;;The directory names are the MAST names. The second argument needs to
;;be a name recognizable by SIMBAD.

pro lcogt_dr7

  lcogt_phot,'/astro/ullyses/lcogt_data/V-BP-TAU/','V* BP Tau'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-GM-AUR/','V* GM Aur'

  lcogt_uphot,'/astro/ullyses/lcogt_data/V-BP-TAU/','V* BP Tau'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-GM-AUR/','V* GM Aur'

  lcogt_combine,'V-BP-TAU'
  lcogt_combine,'V-GM-AUR'

end
