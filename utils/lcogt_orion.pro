;;This is a wrapper that calls lcogt_phot.pro 13 times, once for each
;;Orion target

pro lcogt_orion
 
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-17/','CVSO 17'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-36/','CVSO 36'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-58/','CVSO 58'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-90/','CVSO 90'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-104/','CVSO 104'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-107/','CVSO 107'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-109/','CVSO 109'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-146/','CVSO 146'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-165/','CVSO 165'
  lcogt_phot,'/astro/ullyses/lcogt_data/CVSO-176/','CVSO 176'
  lcogt_phot,'/astro/ullyses/lcogt_data/V505-ORI/','V505 Ori'
  lcogt_phot,'/astro/ullyses/lcogt_data/V510-ORI/','V510 Ori'
  lcogt_phot,'/astro/ullyses/lcogt_data/V-TX-ORI/','V* TX Ori'

end
