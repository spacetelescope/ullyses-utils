;;The main program, lcogt_phot, is at the bottom. It calls photometry,
;;which then calls get_counts, fit_counts, and get_mag. The program
;;dcoord converts a string of sexagesimal coordinates into a vector of
;;three decimal coordinates. Another program, find_mjd, determines the
;;starting MJD of the observation.

function dcoord,scoord,RA=ra

  ;;Examples
  ;;IDL> print,dcoord('18:20:22',/ra)
  ;;     275.09167
  ;;IDL> print,dcoord('+18:20:22')    
  ;;     18.339444
  
  if keyword_set(ra) then begin
     d=strmid(scoord,0,2)
     m=strmid(scoord,3,2)
     s=strmid(scoord,6)
     dc=ten(d,m,s)*15
  endif else begin
     d=strmid(scoord,0,3)
     m=strmid(scoord,4,2)
     s=strmid(scoord,7)
     dc=ten(d,m,s)
  endelse

  return,dc

end

function find_mjd,date_obs

  ;;We want to record the starting and ending MJD of the observation
  ;;to enough precision such that subtracting the start from the end
  ;;gives the correct exposure time to the nearest millisecond, as
  ;;reported in the header. The header keyword MJD-OBS is not precise
  ;;enough for this, but we can use DATE-OBS.

  ;;DATE-OBS is a string, so extract year, month, day, etc
  yr=strmid(date_obs,0,4)
  mo=strmid(date_obs,5,2)
  dy=strmid(date_obs,8,2)
  hr=strmid(date_obs,11,2)
  mn=strmid(date_obs,14,2)
  sc=strmid(date_obs,17)

  ;;convert this into an mjd
  mjd=julday(mo,dy,yr,hr,mn,sc)-2400000.5

  return,mjd

end

function get_counts,star,calimage,catfile,exptime_cal,airmass_cal

  ;;return RA, Dec, counts of calibration targets

  print,calimage
  im=mrdfits(calimage,0,hdr,/si)

  ;;Later we'll need the exposure time and airmass of the
  ;;calibration image
  exptime_cal=sxpar(hdr,'EXPTIME')
  airmass_cal=sxpar(hdr,'AIRMASS')

  ;;check if WCS is well determined (0 if ok)
  if sxpar(hdr,'WCSERR') ne 0 then begin

     ;;borrow an image with good WCS
     case star of
        'V* BP Tau': good=datadir+'V-BP-TAU-CAL/ogg0m406-kb27-20210909-0216-e91.fits.fz'
        'V* GM Aur': good=datadir+'V-GM-AUR-CAL/ogg0m404-kb82-20211010-0250-e91.fits.fz'
        'V* RU Lup': good=datadir+'V-RU-LUP-CAL/coj0m403-kb24-20210816-0046-e91.fits.fz'
        'V* TW Hya': good=datadir+'V-TW-HYA-CAL/cpt0m407-kb84-20210403-0120-e91.fits.fz'
     endcase

     ;;copy astrometry from good to bad
     hg=headfits(good,exten=1,/si)
     extast,hg,goodastr
     putast,hdr,goodastr

     ;;images may still have different centers
     badra=dcoord(sxpar(hdr,'RA'),/ra)
     baddec=dcoord(sxpar(hdr,'DEC'))
     goodra=dcoord(sxpar(hg,'RA'),/ra)
     gooddec=dcoord(sxpar(hg,'DEC'))

     deltara=badra-goodra
     deltadec=baddec-gooddec

     readcol,catfile,delim=';',/preserve_null,format='x,x,d,d,x,x,x,x,x,x,x,x,x,x,x,x,d',ra,dec,umag,/si
     g=sort(umag)
     ra=ra[g[0:2]]
     dec=dec[g[0:2]]
     adxy,hdr,ra-deltara,dec-deltadec,x,y
     cntrd,im,x,y,xcen,ycen,5,extendbox=41,/silent
     found=where(xcen gt 0,nfound)

     if nfound gt 2 then begin
        starast,ra,dec,xcen,ycen,hdr=hdr
     endif else begin
        print,'% Bad WCS'
        return,99
     endelse

  endif

  ;;A small number of images have MJD-OBS = 'UNKNOWN' in their
  ;;headers. We don't actually do anything with this field, but
  ;;xyad.pro crashes on these images, so fix it. The check of whether
  ;;type = 7 catches the case where it's a string, not a double.
  if size(sxpar(hdr,'MJD-OBS'),/type) eq 7 then begin
     correct_mjd=find_mjd(sxpar(hdr,'DATE-OBS'))
     sxaddpar,hdr,'MJD-OBS',correct_mjd
  endif
  
  ;;get catalog list
  readcol,catfile,delim=';',/preserve_null,format='x,x,d,d,x,x,x,x,x,x,x,x,x,x,x,x,d',ra,dec,umag,/si
  adxy,hdr,ra,dec,x,y
  cntrd,im,x,y,xcen,ycen,5,/silent
  found=where(xcen ne -1 and ycen ne -1)
  
  ;;do aperture photometry on those detections
  aper,im,xcen[found],ycen[found],/flux,counts,err,sky,skyerr,1,5,[10,20],[0,0],/si

  ;;convert x and y to RA and Dec
  xyad,hdr,xcen[found],ycen[found],a,d

  ;;return RA, Dec, counts
  data=transpose([[a],[d],[transpose(counts)]])

  return,data

end

function fit_counts,image,sources,catfile,filter,PLOT=plot

  ;;match found sources to catalog sources and fit counts vs mags

  ;;exit if an error happened earlier
  if sources[0] eq 99 then return,99

  ra=sources[0,*]
  dec=sources[1,*]
  counts=sources[2,*]
  n_sources=n_elements(counts)

  ;;get coordinates and magnitudes from external catalog
  readcol,catfile,delim=';',/preserve_null,format='x,x,d,d,x,x,x,x,x,x,x,x,x,x,x,x,d',ra_cat,dec_cat,mag_cat,/si

  fit_counts=!null
  fit_mag=!null
  fit_ra=!null
  fit_dec=!null
  for i=0,n_sources-1 do begin
     gcirc,2,ra[i],dec[i],ra_cat,dec_cat,sep
     ;;match catalog sources to observed sources if < 2 arcsec apart
     if min(sep,msp) lt 2 then begin
        fit_counts=[fit_counts,counts[i]]
        fit_mag=[fit_mag,mag_cat[msp]]
        fit_ra=[fit_ra,ra[i]]
        fit_dec=[fit_dec,dec[i]]
     endif
  endfor

  ;;fit counts vs mag
  x=fit_mag
  y=-2.5*alog10(fit_counts)

  ;;fit a line; can have a slope other than 1 to allow for non-linearity
  ;;remove 3-sigma outliers; newx and newy are retained
  sig=3
  coeff=goodpoly(x,y,1,sig,yfit,newx,newy)

  if keyword_set(plot) then begin
     xrange=[max(x)+0.5,min(x)-0.5]
     yrange=[max(y)+0.5,min(y)-0.5]
     plot,x,y,psym=1,/iso,$
          xrange=xrange,yrange=yrange,$
          title=strmid(catfile,strpos(catfile,'/',/reverse_search)+1)+' '+$
          strmid(image,strpos(image,'/',/reverse_search)+1),$
          xtitle='Magnitude',ytitle='-2.5 log (counts)'
     oplot,newx,newy,psym=1,color=255
     oplot,!x.crange,!x.crange*coeff[1]+coeff[0]
  endif

  print,coeff,format='(2f14.7)'
  return,coeff

end

function get_mag,image,coeff,targ_ra,targ_dec,f0,exptime_cal,airmass_cal,PLOT=plot

  ;;get flux and uncertainty of target from fit in previous step

  ;;exit if an error happened earlier
  if coeff[0] eq 99 then return,99

  im=mrdfits(image,0,hdr,/si)

  ;;We'll need the exposure time and airmass of the science image
  exptime_sci=sxpar(hdr,'EXPTIME')
  airmass_sci=sxpar(hdr,'AIRMASS')

  ;;magnitudes per airmass at u band; see Table 3 of Fukugita et al. (1996, AJ, 111, 1748)
  ku=0.582

  ;;corrections in magnitudes
  exptime_corr=-2.5*alog10(exptime_cal/exptime_sci)
  airmass_corr=ku*(airmass_cal-airmass_sci)
  
  ;;print,exptime_corr,airmass_sci,airmass_cal,airmass_corr
  
  ;;A small number of images have MJD-OBS = 'UNKNOWN' in their
  ;;headers. We don't actually do anything with this field, but
  ;;xyad.pro crashes on these images, so fix it. The check of whether
  ;;type = 7 catches the case where it's a string, not a double.
  if size(sxpar(hdr,'MJD-OBS'),/type) eq 7 then begin
     correct_mjd=find_mjd(sxpar(hdr,'DATE-OBS'))
     sxaddpar,hdr,'MJD-OBS',correct_mjd
  endif

  ;;get astrometry from the next image, which is V band
  startpos=strpos(image,'/',/reverse_search)+1
  init_str=strmid(image,0,startpos+23)
  imagenum=strmid(image,startpos+23,4)
  last_str='-e91.fits.fz'
  nextimage=init_str+string(imagenum+1,format='(i04)')+last_str
  next_exists=file_test(nextimage)
  if next_exists then begin

     hv=headfits(nextimage,exten=1)
     extast,hv,hvastro
     putast,hdr,hvastro
    
     ;;convert targ RA and Dec to x and y
     adxy,hdr,targ_ra,targ_dec,x,y

     ;;do aperture photometry (centroid first)
     cntrd,im,x,y,xcen,ycen,7,/silent
     if xcen eq -1 or ycen eq -1 then return,99 ;;source not found for whatever reason
     aper,im,xcen,ycen,/flux,mags,err,sky,skyerr,1,5,[10,20],[0,0],/si
     counts=mags[0]
     cerr=err[0]

  endif else begin

     print,'% No V image for astrometry'
     return,99

  endelse

  mag=(-2.5*alog10(counts)-coeff[0])/coeff[1]
  ;;correct for exposure time and airmass
  mag=mag+exptime_corr+airmass_corr
  ;;convert to flux, corrected for exposure time and airmass
  flux=f0*10^(-0.4*mag)
  ;;uncertainty (assumes uncertainty in the flux of the target dominates)
  unc=cerr/counts*flux/coeff[1]

  if keyword_set(plot) then begin
     oplot,!x.crange,[1,1]*(-2.5*alog10(counts)),linestyle=1
     oplot,[1,1]*mag,!y.crange,linestyle=1
  endif

  ;;print,counts,cerr,mag,format='(3f14.5)'
  
  return,[flux,unc]

end

function photometry,target,image,calimage,catfile,filter,targ_ra,targ_dec,f0,PLOT=plot

  ;;return RA, Dec, counts of calibration targets
  sources=get_counts(target,calimage,catfile,exptime_cal,airmass_cal)
  
  ;;match found sources to catalog sources and fit counts vs mags
  coeff=fit_counts(calimage,sources,catfile,filter,PLOT=plot)

  ;;get flux and uncertainty of target from fit in previous step
  flux=get_mag(image,coeff,targ_ra,targ_dec,f0,exptime_cal,airmass_cal,PLOT=plot)

  return,flux

end

pro lcogt_uphot,imagedir,target,PLOT=plot,datadir

  ;;uncomment when debugging to close any output files
  close,/all

  if n_params() ne 2 then begin
     print,'% lcogt_phot, imagedir, target'
     return
  endif

  ;;Location of the SDSS tables and tables that map science images to
  ;;calibration images
  catalogdir='data/lcogt_catalogs/'
  if ~file_test(catalogdir) then begin
     print,'% Catalog directory '+catalogdir+' not found.'
     print,'% Edit the code to point elsewhere if need be.'
  endif
  
  ;;Get coordinates of target from SIMBAD
  querysimbad,target,targ_ra,targ_dec,FOUND=found
  if ~found then begin
     print,'% Target '+target+' not found in SIMBAD'
     print,'% Note: variable star names need a V* in front'
     return
  endif

  ;;Make an output filename from the MAST name embedded in the
  ;;directory name
  tn1=strmid(imagedir,0,strpos(imagedir,'/',/reverse_search))
  targname=strmid(tn1,strpos(tn1,'/',/reverse_search)+1)

  photfile=targname+'_uphot.txt'

  ;;Get target, filter, MJD (start and stop) for all images
  all_files=file_search(imagedir+'*.fits*',count=n_all)
  print,'% Found '+strtrim(n_all,2)+' images in '+imagedir
  if n_all eq 0 then return
  all_targets=!null
  all_filters=!null
  all_start=!null
  all_end=!null
  for i=0,n_all-1 do begin
     h=headfits(all_files[i],exten=1)
     object=repchr(strtrim(sxpar(h,'OBJECT'),2),' ','-')
     filter=strtrim(sxpar(h,'FILTER1'),2)
     mjd=find_mjd(sxpar(h,'DATE-OBS'))
     exptime=sxpar(h,'EXPTIME')
     all_targets=[all_targets,object]
     all_filters=[all_filters,filter]
     all_start=[all_start,mjd]
     ;;ending MJD is the starting one plus the exp time in days
     all_end=[all_end,mjd+exptime/3600/24]
  endfor

  ;;Sort all images by MJD
  chron=sort(all_start)
  all_files=all_files[chron]
  all_targets=all_targets[chron]
  all_filters=all_filters[chron]
  all_start=all_start[chron]
  all_end=all_end[chron]

  ;;Do all up band in MJD order
  filters=['up']
  openw,1,photfile
  printf,1,';File (Wave in A; Flux in erg/s/cm2/A)','MJD_start','MJD_end','Wave','Flux','Unc',$
         format='(a-39,2("  ",a-15),"  ",a-4,2("  ",a-10))'
  for i=0,0 do begin

     print,'% Doing photometry at '+filters[i]

     ;;data from Table 2A of Fukugita et al. (1996, AJ, 111, 1748)
     if filters[i] eq 'up' then begin
        wave=3560
        f0=1.852e-9 ;;erg/s/cm2/A, AB system
     endif

     ;;Identify calibration catalog file
     catfile=catalogdir+targname+'-CAL_sdss.txt'

     if ~file_test(catfile) then begin
        print,'% Calibration catalog file '+catfile+' not found'
        close,/all
        return
     endif

     ;;Identify file that maps science images to calibration images
     caltable=catalogdir+'cal_fields_'+targname+'.csv'
     
     if ~file_test(caltable) then begin
        print,'% Calibration image list '+caltable+' not found'
        close,/all
        return
     endif

     readcol,caltable,delim=',',format='x,a,a',scifiles,calfiles,/si

     ;;Get started on the photometry
     dophot=where(all_filters eq filters[i],nphot)
     if nphot eq 0 then continue
     mjd1=make_array(nphot,/double)
     mjd2=make_array(nphot,/double)
     fluxes=make_array(2,nphot,/double)
     for j=0,nphot-1 do begin
        cal_avail=where(scifiles eq all_files[dophot[j]],ncal)
        if ncal gt 0 then calimage=calfiles[cal_avail] else continue
        mjd1[j]=all_start[dophot[j]]
        mjd2[j]=all_end[dophot[j]]
        fluxes[*,j]=photometry(target,all_files[dophot[j]],calimage,catfile,filters[i],targ_ra,targ_dec,f0,PLOT=plot)
        ;;remove path from filename
        filename=strmid(all_files[dophot[j]],strpos(all_files[dophot[j]],'/',/reverse_search)+1)
        ;;Only print if a valid flux was measured and S/N > 5
        if fluxes[0,j] ne 99 and fluxes[0,j]/fluxes[1,j] gt 5 then $
        printf,1,filename,mjd1[j],mjd2[j],wave,fluxes[*,j],format='(a-39,2d17.9,i6,2e12.4)'
     endfor

  endfor

  close,1
  print,'% Wrote '+photfile

end
