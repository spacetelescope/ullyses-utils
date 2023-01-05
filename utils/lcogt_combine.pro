;;Separate files are created for u photometry and Vi photometry. This
;;script combines them into a single file.

pro lcogt_combine,star

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

  openw,1,filevi
  printf,1,';File (Wave in A; Flux in erg/s/cm2/A)','MJD_start','MJD_end','Wave','Flux','Unc',$
         format='(a-39,2("  ",a-15),"  ",a-4,2("  ",a-10))'
  for i=0,nu-1 do printf,1,imu[i],mjd0u[i],mjd1u[i],wu[i],fu[i],uu[i],format=fmt
  for i=0,nvi-1 do printf,1,imvi[i],mjd0vi[i],mjd1vi[i],wvi[i],fvi[i],uvi[i],format=fmt
  close,1

  spawn,'rm '+fileu
  print,'% Incorporated '+fileu+' into '+filevi

end
