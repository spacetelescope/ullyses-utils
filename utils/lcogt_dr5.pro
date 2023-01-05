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

  combine_uvi,'V-TW-HYA'
  combine_uvi,'V-RU-LUP'
  combine_uvi,'V-BP-TAU'
  combine_uvi,'V-GM-AUR'

end

pro combine_uvi,star

  fileu=star+'_uphot.txt'
  filevi=star+'_phot.txt'

  if ~file_test(fileu) then begin
     print,'% File '+fileu+' not found'
     return
  endif

  if ~file_test(filevi) then begin
     print,'% File '+filevi+' not found'
     return
  endif

  readcol,fileu,format='(a,d,d,i,f,f)',imu,mjd0u,mjd1u,wu,fu,uu,/si,count=nu
  readcol,filevi,format='(a,d,d,i,f,f)',imvi,mjd0vi,mjd1vi,wvi,fvi,uvi,/si,count=nvi

  fmt='(a-39,2d17.9,i6,2e12.4)'

  openw,1,'x'+filevi
  printf,1,';File (Wave in A; Flux in erg/s/cm2/A)','MJD_start','MJD_end','Wave','Flux','Unc',$
         format='(a-39,2("  ",a-15),"  ",a-4,2("  ",a-10))'
  for i=0,nu-1 do printf,1,imu[i],mjd0u[i],mjd1u[i],wu[i],fu[i],uu[i],format=fmt
  for i=0,nvi-1 do printf,1,imvi[i],mjd0vi[i],mjd1vi[i],wvi[i],fvi[i],uvi[i],format=fmt
  close,1

  print,'% Wrote '+filevi

end
