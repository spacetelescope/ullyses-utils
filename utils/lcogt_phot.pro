;;the main program, lcogt_phot, is at the bottom
;;it calls photometry, which in turn calls get_counts, fit_counts, and get_mag

function get_counts,image

  ;;return RA, Dec, counts of calibration targets
  
  print,image
  im=mrdfits(image,0,hdr,/si)

  ;;check if WCS is well determined (0 if ok)
  if sxpar(hdr,'WCSERR') ne 0 then begin
     print,'% Bad WCS'
     return,99
  endif
  
  ;;get a list of detections from the 1st extension
  tab=mrdfits(image,1,htab,/si)
  
  ;;do aperture photometry on those detections
  aper,im,tab.x,tab.y,/flux,counts,err,sky,skyerr,1,5,[10,20],[0,0],/si

  ;;convert x and y to RA and Dec
  xyad,hdr,tab.x,tab.y,a,d

  ;;return RA, Dec, counts
  data=transpose([[a],[d],[transpose(counts)]])

  return,data

end

function fit_counts,image,sources,catfile,filter

  ;;match found sources to catalog sources and fit counts vs mags

  ;;exit if an error happened earlier
  if sources[0] eq 99 then return,99
  
  ra=sources[0,*]
  dec=sources[1,*]
  counts=sources[2,*]
  n_sources=n_elements(counts)

  ;;get coordinates and magnitudes from external catalog
  ;;due to the format keyword, only lines with both V and i mags are read
  readcol,catfile,format='(d,x,d,x,f,x,x,x,x,x,x,x,x,x,x,x,x,x,x,f,x,x)',delim=', ',$
          ra_cat,dec_cat,v_cat,i_cat,/si,count=ctmag
  if filter eq 'V' then mag_cat=v_cat else mag_cat=i_cat
  
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
  
  xrange=[max(mag_cat)+0.5,min(mag_cat)-0.5]
  plot,x,y,psym=1,/iso,$
       xrange=xrange,yrange=xrange*1.15+coeff[0],$
       title=strmid(catfile,strpos(catfile,'/',/reverse_search)+1)+' '+$
       strmid(image,strpos(image,'/',/reverse_search)+1),$
       xtitle='Magnitude',ytitle='-2.5 log (counts)'

  oplot,newx,newy,psym=1,color=255
  oplot,!x.crange,!x.crange*coeff[1]+coeff[0]

  print,coeff,format='(2f14.7)'

  return,coeff
  
end

function get_mag,image,coeff,targ_ra,targ_dec,f0

  ;;get flux and uncertainty of target from fit in previous step
  
  ;;exit if an error happened earlier
  if coeff[0] eq 99 then return,99
  
  im=mrdfits(image,0,hdr,/si)

  ;;convert targ RA and Dec to x and y
  adxy,hdr,targ_ra,targ_dec,x,y

  ;;do aperture photometry (centroid first)
  cntrd,im,x,y,xcen,ycen,7
  if xcen eq -1 or ycen eq -1 then return,99 ;;source not found for whatever reason
  aper,im,xcen,ycen,/flux,mags,err,sky,skyerr,1,5,[10,20],[0,0],/si
  counts=mags[0]
  cerr=err[0]

  mag=(-2.5*alog10(counts)-coeff[0])/coeff[1]
  ;;convert to flux
  flux=f0*10^(-0.4*mag)
  ;;uncertainty (assumes uncertainty in the flux of the target dominates)
  unc=cerr/counts*flux/coeff[1]
  
  oplot,!x.crange,[1,1]*(-2.5*alog10(counts)),linestyle=1
  oplot,[1,1]*mag,!y.crange,linestyle=1

  ;;print,counts,cerr,mag,format='(3f14.5)'

  return,[flux,unc]

end

function photometry,image,catfile,filter,targ_ra,targ_dec,f0

  ;;return RA, Dec, counts of calibration targets
  sources=get_counts(image)

  ;;match found sources to catalog sources and fit counts vs mags
  coeff=fit_counts(image,sources,catfile,filter)

  ;;get flux and uncertainty of target from fit in previous step
  flux=get_mag(image,coeff,targ_ra,targ_dec,f0)

  return,flux

end

pro lcogt_phot,imagedir,target

  ;;uncomment when debugging to close any output files
  ;;close,/all
  
  if n_params() ne 2 then begin
     print,'% lcogt_phot, imagedir, target'
     return
  endif

  ;;Location of the APASS tables
  catalogdir='~/lcogt_phot/catalogs/'

  ;;Get coordinates of target from SIMBAD
  querysimbad,target,targ_ra,targ_dec,FOUND=found
  if ~found then begin
     print,'% Target '+target+' not found in SIMBAD'
     print,'% Note: variable star names need a V* in front'
     return
  endif

  ;;Make a reasonable output filename --
  ;;turn * into -, strip whitespace, make it lowercase
  targname=strlowcase(repstr(repstr(target,'*','-'),' '))
  photfile=targname+'_phot.txt'

  ;;Get target, filter, date for all images
  all_files=file_search(imagedir+'*.fits*',count=n_all)
  print,'% Found '+strtrim(n_all,2)+' images in '+imagedir
  if n_all eq 0 then return
  all_targets=!null
  all_filters=!null
  all_dates=!null
  for i=0,n_all-1 do begin
     h=headfits(all_files[i],exten=1)
     object=repchr(strtrim(sxpar(h,'OBJECT'),2),' ','-')
     filter=strtrim(sxpar(h,'FILTER1'),2)
     mjd=sxpar(h,'MJD-OBS')
     all_targets=[all_targets,object]
     all_filters=[all_filters,filter]
     all_dates=[all_dates,mjd]
  endfor

  ;;Sort all images by MJD
  chron=sort(all_dates)
  all_files=all_files[chron]
  all_targets=all_targets[chron]
  all_filters=all_filters[chron]
  all_dates=all_dates[chron]

  ;;Do all V band in MJD order, then all ip band in MJD order
  filters=['V','ip']
  openw,1,photfile
  printf,1,';File (Wave in A; Flux in erg/s/cm2/A)','MJD','Wave','Flux','Unc',format='(a-39,"  ",a-10,"  ",a-4,2("  ",a-10))'
  for i=0,1 do begin

     print,'% Doing photometry at '+filters[i]

     ;;data from Table A2 of Bessell et al. (1998, A&A, 333, 231)
     if filters[i] eq 'V' then begin
        wave=5450
        f0=3.631e-9 ;;erg/s/cm2/A, Vega system
     endif
     ;;data from Table 2A of Fukugita et al. (1996, AJ, 111, 1748)
     if filters[i] eq 'ip' then begin
        wave=7670
        f0=1.852e-9 ;;erg/s/cm2/A, AB system
     endif
        
     ;;Identify calibration catalog file
     catfile=catalogdir+targname+'_apass.txt'

     if ~file_test(catfile) then begin
        print,'% Calibration catalog file '+catfile+' not found'
        close,/all
        return
     endif

     ;;Get started on the photometry
     dophot=where(all_filters eq filters[i],nphot)
     if nphot eq 0 then continue
     mjds=make_array(nphot,/double)
     fluxes=make_array(2,nphot,/double)
     for j=0,nphot-1 do begin
        mjds[j]=all_dates[dophot[j]]
        fluxes[*,j]=photometry(all_files[dophot[j]],catfile,filters[i],targ_ra,targ_dec,f0)
        ;;remove path from filename
        filename=strmid(all_files[dophot[j]],strpos(all_files[dophot[j]],'/',/reverse_search)+1)
        ;;Only print if a valid flux was measured
        if fluxes[0,j] ne 99 then $
           printf,1,filename,mjds[j],wave,fluxes[*,j],format='(a-39,d12.4,i6,2e12.4)'
     endfor

  endfor

  close,1
  print,'% Wrote '+photfile

end
