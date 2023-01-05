;;This wrapper calls lcogt_phot.pro once for each DR6 target.
;;It also calls lcogt_uphot.pro once for each DR6 target with u-band data.
;;Then it runs a script that combines the Vi and u output.

;;The directory names are the MAST names. The second argument needs to
;;be a name recognizable by SIMBAD.

pro lcogt_dr6

  lcogt_phot,'/astro/ullyses/lcogt_data/V-TX-ORI/','V* TX Ori'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ19/','Sz 19'
  lcogt_phot,'/astro/ullyses/lcogt_data/HD-104237E/','HD 104237E'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-SY-CHA/','V* SY Cha'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-TW-HYA/','V* TW Hya'
  lcogt_phot,'/astro/ullyses/lcogt_data/SSTC2DJ161243-381503/','SSTc2d J161243-381503'
  lcogt_phot,'/astro/ullyses/lcogt_data/CHX18N/','CHX 18N'
  lcogt_phot,'/astro/ullyses/lcogt_data/HN5/','Hn 5'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-IN-CHA/','V* IN Cha'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-VZ-CHA/','V* VZ Cha'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-WZ-CHA/','V* WZ Cha'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-XX-CHA/','V* XX Cha'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ129/','Sz 129'
  lcogt_phot,'/astro/ullyses/lcogt_data/SSTC2DJ161344-373646/','SSTc2d J161344-373646'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ84/','Sz 84'
  lcogt_phot,'/astro/ullyses/lcogt_data/RXJ1556-3655/','RX J1556-3655'
  lcogt_phot,'/astro/ullyses/lcogt_data/RXJ1843-3532/','RX J1843-3532'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ100/','Sz 100'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ103/','Sz 103'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ104/','Sz 104'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ110/','Sz 110'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ114/','Sz 114'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ115/','Sz 115'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ117/','Sz 117'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ97/','Sz 97'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ98/','Sz 98'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ99/','Sz 99'
  lcogt_phot,'/astro/ullyses/lcogt_data/SZ82/','Sz 82'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-RU-LUP','V* RU Lup'
  lcogt_phot,'/astro/ullyses/lcogt_data/RX J1852-3700/','RX J1852-3700'

  lcogt_uphot,'/astro/ullyses/lcogt_data/V-TW-HYA/','V* TW Hya'
  lcogt_uphot,'/astro/ullyses/lcogt_data/V-RU-LUP/','V* RU Lup'
  lcogt_uphot,'/astro/ullyses/lcogt_data/SZ82/','Sz 82'

  lcogt_combine,'V-TW-HYA'
  lcogt_combine,'V-RU-LUP'
  lcogt_combine,'SZ82'

end
