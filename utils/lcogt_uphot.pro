;;The main program, lcogt_ucounts, is at the bottom. It calls photometry,
;;which then calls get_counts, get_caldata, and get_mag. Another
;;program, find_mjd, determines the starting MJD of the observation.

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

function get_counts,image,targ_ra,targ_dec

  ;;return counts of target

  print,image
  im=mrdfits(image,0,hdr,/si)
  tel=sxpar(hdr,'TELID')

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
     if strmid(tel,0,2) eq '1m' then fwhm=9 else fwhm=7
     cntrd,im,x,y,xcen,ycen,fwhm,/silent
     if xcen eq -1 or ycen eq -1 then return,99 ;;source not found for whatever reason
     aper,im,xcen,ycen,/flux,mags,err,sky,skyerr,1,5,[10,20],[0,0],/si
     counts=mags[0]
     cerr=err[0]

  endif else begin

     if sxpar(hdr,'WCSERR') eq 0 then begin

        ;;convert targ RA and Dec to x and y
        adxy,hdr,targ_ra,targ_dec,x,y

        ;;do aperture photometry (centroid first)
        if strmid(tel,0,2) eq '1m' then fwhm=9 else fwhm=7
        cntrd,im,x,y,xcen,ycen,fwhm,/silent
        if xcen eq -1 or ycen eq -1 then return,99 ;;source not found for whatever reason
        aper,im,xcen,ycen,/flux,mags,err,sky,skyerr,1,5,[10,20],[0,0],/si
        counts=mags[0]
        cerr=err[0]

     endif else begin

        print,'% No V image for astrometry'
        return,99

     endelse

  endelse

  return,[counts,cerr]

end

function get_caldata,counts,catfile,calimage,PLOT=plot

  ;;fit counts vs mags in calibration field

  ;;exit if an error happened earlier
  if counts[0] eq 99 then return,99

  ;;need calibration exposure time, airmass, and telescope
  im=mrdfits(calimage,0,h,/si)
  s=size(im)
  calexptime=sxpar(h,'EXPTIME')
  calairmass=sxpar(h,'AIRMASS')
  caltel=sxpar(h,'TELID')

  ;;several steps are necessary to accomodate images where the LCOGT
  ;;automated WCS assignment fails

  ;;get tabulated x, y from reference image
  if strmid(caltel,0,2) eq '1m' then catfile=repstr(catfile,'.csv','-1m.csv')
  readcol,catfile,format='(x,d,f,f,f)',decref,uref,xref,yref,/si,delim=',',count=nbest
  ;;If there are two cal fields, ignore entries from the wrong one
  tn1=strmid(catfile,strpos(catfile,'/',/reverse_search))
  star=strmid(tn1,strpos(tn1,'/',/reverse_search)+1,8)
  if (star eq 'V-BP-TAU' or star eq 'V-GM-AUR') then begin
     north=where(decref gt 30,ctnorth,comp=south,ncomp=ctsouth)
     if sxpar(h,'MJD-OBS') gt 59700 then begin
        uref=uref[north]
        xref=xref[north]
        yref=yref[north]
        nbest=ctnorth
     endif else begin
        uref=uref[south]
        xref=xref[south]
        yref=yref[south]
        nbest=ctsouth
     endelse
  endif

  catfile=repstr(catfile,'-1m.csv','.csv')
  umin=min(uref,bright)
  xref0=xref[bright]
  yref0=yref[bright]

  ;;in some calibration images, the location of the brightest star is
  ;;very different from that in the reference image
  if star eq 'V-BP-TAU' and strmid(sxpar(h,'DATE-OBS'),0,7) eq '2021-07' then begin
     xref=xref-600
     yref=yref+200
     xref0=xref0-600
     yref0=yref0+200
  endif
  if star eq 'V-GM-AUR' and strmid(sxpar(h,'DATE-OBS'),0,10) eq '2021-10-05' then begin
     xref=xref+300
     yref=yref-60
     xref0=xref0+300
     yref0=yref0-60
  endif

  ;;find the brightest star in a box around its expected location
  bsize=250
  sub=im[xref0-bsize>0:xref0+bsize<s[1]-1,yref0-bsize>0:yref0+bsize<s[2]-1]
  find,sub,x,y,flux,sharp,round,1.2*stddev(sub),7,[-0.8,0.8],[0.1,0.9],/silent
  aper,sub,x,y,flux,err,sky,skyerr,1,5,[10,20],[0,0],/flux,/silent
  fmax=max(flux,q)

  ;;calculate offset from expected x, y
  xoff=x[q]-bsize
  yoff=y[q]-bsize

  ;;apply offset to other x, y
  xlook=xref+xoff
  ylook=yref+yoff

  ;;find other stars
  bsize=100
  xs=-1
  ys=-1
  fmax=make_array(nbest)
  for j=0,nbest-1 do begin

     if xlook[j] lt 0 or xlook[j] gt s[1] or $
        ylook[j] lt 0 or ylook[j] gt s[2] then continue

     xmin=(xlook[j]-bsize)>0<(s[1]-2)
     xmax=(xlook[j]+bsize)>0<(s[1]-1)>(xmin+1)
     ymin=(ylook[j]-bsize)>0<(s[2]-2)
     ymax=(ylook[j]+bsize)>0<(s[2]-1)>(ymin+1)

     th=im[xmin:xmax,ymin:ymax]
     resistant_mean,th,3,mean,sigma

     find,th,xs,ys,flux,sharp,round,30*sigma,7,[-0.8,0.8],[0.1,0.9],/silent

     p=where(xs gt 0 and ys gt 0,np)
     if np gt 0 then begin
        aper,im,xs[p]+xmin,ys[p]+ymin,flux,err,sky,skyerr,1,5,[10,20],[0,0],/flux,/silent
        fmax[j]=max(flux,q)
     endif

  endfor

  z=where(fmax gt 1100,ctz)

  ;;fit counts vs mag
  if ctz gt 1 then begin
     x=uref[z]
     y=-2.5*alog10(fmax[z])
     ;;fit a line; can have a slope other than 1 to allow for non-linearity
     ;;remove 1.5-sigma outliers; newx and newy are retained
     sig=1.5
     coeff=goodpoly(x,y,1,sig,yfit,newx,newy)
  endif else return,99

  if keyword_set(plot) then begin
     xrange=[max(uref[z])+0.5,min(uref[z])-0.5]
     plot,x,y,psym=1,/iso,$
          xrange=xrange,yrange=xrange*coeff[1]+coeff[0],$
          title=strmid(catfile,strpos(catfile,'/',/reverse_search)+1)+' '+$
          strmid(calimage,strpos(calimage,'/',/reverse_search)+1),$
          xtitle='Magnitude',ytitle='-2.5 log (counts)'
     oplot,newx,newy,psym=1,color=255
     oplot,!x.crange,!x.crange*coeff[1]+coeff[0]
  endif

  print,coeff,format='(2f14.7)'

  return,[coeff[0],coeff[1],calexptime,calairmass]

end

function get_mag,counts,caldata,f0,exptime,airmass,PLOT=plot

  ;;get flux and uncertainty of target from fit in previous step

  ;;exit if an error happened earlier
  if caldata[0] eq 99 then return,99

  ;;magnitudes per airmass at u band; see Table 3 of Fukugita et al. (1996, AJ, 111, 1748)
  ku=0.582
  ;;airmass scaling
  airmass_corr=ku*(caldata[3]-airmass)

  ;;exposure time scaling
  exptime_corr=-2.5*alog10(caldata[2]/exptime)

  ;;scale by counts->flux law
  mag=(-2.5*alog10(counts[0])-caldata[0])/caldata[1]

  ;;correct for airmass and exposure time
  mag_corr=mag+airmass_corr+exptime_corr
  ;;convert to flux
  flux=f0*10^(-0.4*mag_corr)
  ;;uncertainty (assumes uncertainty in the flux of the target dominates)
  unc=counts[1]/counts[0]*flux/caldata[1]

  if keyword_set(plot) then begin
     oplot,!x.crange,[1,1]*(-2.5*alog10(counts[0])),linestyle=1
     oplot,[1,1]*mag,!y.crange,linestyle=1
  endif

  return,[flux,unc]

end

function photometry,image,catfile,targ_ra,targ_dec,f0,exptime,airmass,calimage,PLOT=plot

  ;;return counts of target
  counts=get_counts(image,targ_ra,targ_dec)

  ;;get calibration airmass and exposure time, and fit counts vs mags
  caldata=get_caldata(counts,catfile,calimage,PLOT=plot)

  ;;get flux and uncertainty of target from fit in previous step
  flux=get_mag(counts,caldata,f0,exptime,airmass,PLOT=plot)

  return,flux

end

pro lcogt_uphot,imagedir,target,PLOT=plot

  ;;uncomment when debugging to close any output files
  ;;close,/all

  if n_params() ne 2 then begin
     print,'% lcogt_uphot, imagedir, target'
     return
  endif

  ;;Location of the calibration files
  catalogdir='data/lcogt_catalogs/'
  if ~file_test(catalogdir) then begin
     print,'% Catalog directory '+catalogdir+' not found.'
     print,'% Edit the code to point elsewhere if need be.'
     return
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

  ;;Identify calibration catalog file
  catfile=catalogdir+targname+'-CAL_best_stars.csv'
  if ~file_test(catfile) then begin
     print,'% Calibration catalog file '+catfile+' not found'
     close,/all
     return
  endif

  ;;Get list of cal images
  cal_list=catalogdir+targname+'_cal_fields.csv'
  if ~file_test(cal_list) then begin
     print,'% Calibration catalog file '+cal_list+' not found'
     close,/all
     return
  endif
  readcol,cal_list,format='(d,a,a)',mjd,sciimages,calimages,/si,delim=',',count=ncal

  ;;Get target, filter, MJD (start and stop), cal image (if available) for all images
  all_files=file_search(imagedir+'*.fits*',count=n_all)
  print,'% Found '+strtrim(n_all,2)+' images in '+imagedir
  if n_all eq 0 then return
  all_targets=!null
  all_filters=!null
  all_start=!null
  all_end=!null
  all_exptime=!null
  all_airmass=!null
  all_cal=!null
  for i=0,n_all-1 do begin
     h=headfits(all_files[i],exten=1)
     object=repchr(strtrim(sxpar(h,'OBJECT'),2),' ','-')
     filter=strtrim(sxpar(h,'FILTER'),2)
     mjd=find_mjd(sxpar(h,'DATE-OBS'))
     exptime=sxpar(h,'EXPTIME')
     airmass=sxpar(h,'AIRMASS')
     calnum=where(sciimages eq all_files[i],ncalim)
     all_targets=[all_targets,object]
     all_filters=[all_filters,filter]
     all_start=[all_start,mjd]
     ;;ending MJD is the starting one plus the exp time in days
     all_end=[all_end,mjd+exptime/3600/24]
     all_exptime=[all_exptime,exptime]
     all_airmass=[all_airmass,airmass]
     if ncalim eq 1 then all_cal=[all_cal,calimages[calnum[0]]] else all_cal=[all_cal,'']
  endfor

  ;;Sort all images by MJD
  chron=sort(all_start)
  all_files=all_files[chron]
  all_targets=all_targets[chron]
  all_filters=all_filters[chron]
  all_start=all_start[chron]
  all_end=all_end[chron]
  all_exptime=all_exptime[chron]
  all_airmass=all_airmass[chron]
  all_cal=all_cal[chron]

  ;;Do all up band in MJD order
  filters=['up']
  openw,1,photfile
  printf,1,';File (Wave in A; Flux in erg/s/cm2/A)','MJD_start','MJD_end','Wave','Flux','Unc',$
         format='(a-39,2("  ",a-15),"  ",a-4,2("  ",a-10))'
  for i=0,n_elements(filters)-1 do begin

     print,'% Doing photometry at '+filters[i]

     ;;data from Table 2A of Fukugita et al. (1996, AJ, 111, 1748)
     if filters[i] eq 'up' then begin
        wave=3560
        f0=8.595e-9 ;;erg/s/cm2/A, AB system
     endif

     ;;Get started on the photometry
     dophot=where(all_filters eq filters[i] and all_cal ne '',nphot)
     if nphot eq 0 then continue
     mjd1=make_array(nphot,/double)
     mjd2=make_array(nphot,/double)
     fluxes=make_array(2,nphot,/double)
     for j=0,nphot-1 do begin
        mjd1[j]=all_start[dophot[j]]
        mjd2[j]=all_end[dophot[j]]
        fluxes[*,j]=photometry(all_files[dophot[j]],catfile,targ_ra,targ_dec,f0,$
                               all_exptime[dophot[j]],all_airmass[dophot[j]],all_cal[dophot[j]],$
                               PLOT=plot)
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
