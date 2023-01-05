;;This wrapper calls lcogt_phot.pro once for each DR5 target.
;;It also calls lcogt_uphot.pro once for each DR5 target with u-band data.
;;Then it runs a script that combines the Vi and u output.

;;The directory names are the MAST names. The second argument needs to
;;be a name recognizable by SIMBAD.

pro lcogt_dr5

  lcogt_phot,'/astro/ullyses/lcogt_data/V-RU-LUP/','V* RU Lup'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-BP-TAU/','V* BP Tau'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-GM-AUR/','V* GM Aur'
  lcogt_phot,'/astro/ullyses/lcogt_data/RXJ0438.6+1546/','RX J0438.6+1546'
  lcogt_phot,'/astro/ullyses/lcogt_data/V505-ORI/','V505 Ori'
  lcogt_phot,'/astro/ullyses/lcogt_data/RECX-5/','RECX 5'
  lcogt_phot,'/astro/ullyses/lcogt_data/RECX-6/','RECX 6'
  lcogt_phot,'/astro/ullyses/lcogt_data/RECX-9/','RECX 9'

  lcogt_uphot,'/astro/ullyses/lcogt_data/V-TW-HYA/','V* TW Hya'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-RU-LUP/','V* RU Lup'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-BP-TAU/','V* BP Tau'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-GM-AUR/','V* GM Aur'

  lcogt_combine,'V-TW-HYA'
  lcogt_combine,'V-RU-LUP'
  lcogt_combine,'V-BP-TAU'
  lcogt_combine,'V-GM-AUR'

end
