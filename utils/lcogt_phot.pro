;;version control at, and put readme at
;;https://github.com/spacetelescope/ullyses_dp/tree/master/high_level_science_products/high_level_science_products
;;make a branch
;;assign Elaine as reviewer

function get_counts,image

  print,image
  im=mrdfits(image,0,hdr,/si)
  rms=sqrt(median(im^2))

  ;;find sources
  find,im,x,y,counts,sharp,round,5*rms,3,[-1,1],[0.2,1],/si

  ;;do aperture photometry
  aper,im,x,y,/flux,mags,err,sky,skyerr,1,5,[10,20],[0,0],/si

  ;;convert x and y to RA and Dec
  xyad,hdr,x,y,a,d

  data=transpose([[a],[d],[transpose(mags)]])

  return,data

end

function fit_counts,image,sources,catfile

  ra=sources[0,*]
  dec=sources[1,*]
  counts=sources[2,*]
  n_sources=n_elements(counts)

  ;;get coordinates and magnitudes from external catalog
  readcol,catfile,format='(x,d,d,d)',delim=', ',$
          ra_cat,dec_cat,mag_cat,/si,count=ctmag

  fit_counts=!null
  fit_mag=!null
  for i=0,n_sources-1 do begin
     gcirc,2,ra[i],dec[i],ra_cat,dec_cat,sep
     ;;match catalog sources to observed sources if < 2 arcsec apart
     if min(sep,msp) lt 2 then begin
        fit_counts=[fit_counts,counts[i]]
        fit_mag=[fit_mag,mag_cat[msp]]
     endif
  endfor

  ;;fit counts vs mag
  x=fit_mag
  y=-2.5*alog10(fit_counts)
  ;;exclude faint sources
  ok=where(x lt 16)
  ;;fit a line
  ;;remove 3-sigma outliers; newx and newy are retained
  sig=3
  coeff=goodpoly(x[ok],y[ok],1,sig,yfit,newx,newy)

  plot,x,y,psym=1,/iso,$
       xrange=[max(x)+0.2,min(x)-0.2],yrange=[max(y)+0.2,min(y)-0.2],$
       title=strmid(catfile,strpos(catfile,'/',/reverse_search)+1)+' '+$
       strmid(image,strpos(image,'/',/reverse_search)+1),$
       xtitle='Magnitude',ytitle='-2.5 log (counts)'
  oplot,newx,newy,psym=1,color=255
  oplot,!x.crange,!x.crange*coeff[1]+coeff[0]
  return,coeff

end

function get_mag,image,coeff,targ_ra,targ_dec

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
  unc=2.5/alog(10)*cerr/counts
  
  oplot,!x.crange,[1,1]*(-2.5*alog10(counts)),linestyle=1
  oplot,[1,1]*mag,!y.crange,linestyle=1
  ;;a=get_kbrd()

  return,[mag,unc]

end

function photometry,image,catfile,targ_ra,targ_dec

  ;;0.4 m pixel size is 0.571 arcsec

  ;;return source RA, Dec, counts, error
  sources=get_counts(image)

  ;;match found sources to catalog sources and fit counts vs mags
  coeff=fit_counts(image,sources,catfile)

  ;;get magnitude of target
  mag=get_mag(image,coeff,targ_ra,targ_dec)

  return,mag

end

pro lcogt_phot,imagedir,target

  if n_params() ne 2 then begin
     print,'% lcogt_phot, imagedir, target'
     return
  endif

  ;;Location of the NOMAD and Skymapper tables
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
     h=headfits(all_files[i])
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
  for i=0,1 do begin

     print,'% Doing photometry at '+filters[i]

     ;;Identify calibration catalog file
     catfile=catalogdir+targname+'-'+filters[i]+'.txt'
     print,catfile

     if ~file_test(catfile) then begin
        print,'% Calibration catalog file '+catfile+' not found'
        close,/all
        return
     endif

     ;;Get started on the photometry
     dophot=where(all_filters eq filters[i],nphot)
     mjds=make_array(nphot,/double)
     mags=make_array(2,nphot,/double)
     for j=0,nphot-1 do begin
        mjds[j]=all_dates[dophot[j]]
        mags[*,j]=photometry(all_files[dophot[j]],catfile,targ_ra,targ_dec)
        if mags [0,j] ne 99 then printf,1,filters[i],mjds[j],mags[*,j],format='(a-2,d12.4,2d9.4)'
     endfor

  endfor

  close,1
  print,'% Wrote '+photfile

end
