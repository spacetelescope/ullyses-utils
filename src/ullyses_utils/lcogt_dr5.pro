;;This is a wrapper that calls lcogt_phot.pro 8 times, once for each
;;DR5 target

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

end
