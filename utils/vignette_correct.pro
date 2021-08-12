pro vignette_correct

;hi! we're comparing these two datasets to adjust the continuum for a spectrum that exhibits vignetting. 

datadir = '/astro/ullyses/custom_cal/v-tw-hya/dr3/g230l/exp/'
outdir = '/astro/ullyses/twhydra_cal/'
;normdata = 'le9d1cdgq_x1d' ;normal dataset
;vigndata = 'le9d1cdeq_x1d' ;vignetted dataset


;readcol,'/Users/tfischer/functional/ullyses/tw_hydra/filenames_crop.txt',bad,good,format = 'A,A',/SILENT ; this reads in the bad/good filenames
readcol,'/astro/ullyses/tfischer/raw_twhydra/filenames.txt',bad,good,format = 'A,A',/SILENT ; this reads in the bad/good filenames

s = size(bad)

for i = 0,s(3)-1 do begin
  ;print,i
  baddat = mrdfits(datadir+bad(i)+'_x1d.fits',1,h1,/SILENT) 
  gooddat = mrdfits(datadir+good(i)+'_x1d.fits',1,h1,/SILENT)
    
  ;baddat = mrdfits(datadir+bad(i)+'_x1d.fits',1,h2)  

;let's take everything out and look at it

  flux1 = [gooddat[0].flux,gooddat[1].flux,gooddat[2].flux] ; get Strip A/B/C fluxes from normal dataset 
  wave1 = [gooddat[0].wavelength,gooddat[1].wavelength,gooddat[2].wavelength] ; " " wavelengths " " 

  flux2 = [baddat[0].flux,baddat[1].flux,baddat[2].flux] ; get Strip A/B/C fluxes from vignetted dataset 
  wave2 = [baddat[0].wavelength,baddat[1].wavelength,baddat[2].wavelength] ; " " wavelengths " " 

; here we select some continuum wavebands in wavelength space to fit a slope to 

;; normal dataset

  cont1a = where(2760 lt wave1 and wave1 lt 2780, count)
  cont1b = where(2820 lt wave1 and wave1 lt 2890, count)

  fluxcont1 = [flux1(cont1a),flux1(cont1b)] ; continuum flux
  wavecont1 = [wave1(cont1a),wave1(cont1b)] ; continuum wavelength


;; vignetted dataset

  cont2a = where(2760 lt wave2 and wave2 lt 2780, count) 
  cont2b = where(2820 lt wave2 and wave2 lt 2890, count) 

  fluxcont2 = [flux2(cont2a),flux2(cont2b)] ; continuum flux
  wavecont2 = [wave2(cont2a),wave2(cont2b)] ; continuum wavelength

  sizew1 = size(wavecont1)
  sizew2 = size(wavecont2)
  
  if (sizew1(1) gt sizew2(1)) then begin
    fluxcont1 = fluxcont1[0:sizew2(1)-1]
    wavecont1 = wavecont1[0:sizew2(1)-1] 
  endif else begin
    fluxcont2 = fluxcont2[0:sizew1(1)-1]
    wavecont2 = wavecont2[0:sizew1(1)-1]
  endelse

;we want to fit lines to the continuum fluxes, 'coeff' gives yfits to plot the lines

  coeff1 = poly_fit(wavecont1,fluxcont1,1,yfit = fit1)
  coeff2 = poly_fit(wavecont2,fluxcont2,1,yfit = fit2)

;here's a window that shows the normal & vignetted data (blue / red) and the selected continuum in the vignetted data
  ;window,i

;  cgplot,wave1,flux1,color = 'blue',xrange = [2750,2900];, yrange = [0,8e-13]
;  cgplot,wave2,flux2/0.92,color = 'red',/overplot
;  cgplot,wavecont2,fluxcont2,thick=2,/overplot

;here's a window that shows the slopes of the continuua in from each dataset, the vignetted data is fainter at short wavelengths
;  window,(i*3)+1

;  cgplot,wavecont2,fit2,thick = 2,color = 'red',xrange = [2750,2900], title = bad(i)+' Uncorrected';, yrange = [1e-14,5e-14]; vignetted data
;  cgplot,wavecont1,fit1,thick = 2,/overplot,color = 'blue' ; normal data

;  cgplot,wave1,flux1,color = 'blue',/overplot ;continuum fit to normal data
;  cgplot,baddat[1].wavelength,baddat[1].flux,color = 'red',/overplot ;continuum fit to *Strip B* of the vignetted data

; let's fit a line to the ratio between the continuum fluxes from both datasets

  result = linfit(wavecont2,fit2/fit1) ; this gives the slope

  compy = result(1)*baddat[1].wavelength + result(0) ; this gives us the y-value of the line across the *Strip B* wavelengths

  ok = where(compy gt 1.,count) ; the ratio goes *over* 1.0 at longer wavelengths, let's find those array values

  compy(ok) = 1. ; aaaaand make them equal to 1.0, now only the vignetted portion of the spectrum will be scaled

; here's a similar distribution to Window 1, except the vignetted flux is corrected on the short wavelength side
;  window,(i*3)+2

  ;cgplot,wave1,flux1,color = 'blue',xrange = [2750,2900], title = bad(i)+' Corrected';, yrange = [1e-14,5e-14]
  ;cgplot,baddat[1].wavelength,baddat[1].flux/compy,color = 'red',/overplot

; This distribution looks good, let's define it as the new flux for Strip B of this vignetted dataset 

  newflux = baddat[1].flux/compy
  baddat[1].flux = newflux

  mwrfits,baddat,outdir+bad(i)+'_x1d_newflux.fits',h2,/create ; and then save the updated vignetted dataset as a new file
  
  scalefile=outdir+bad(i)+'_scale.txt'
  OPENW,1,scalefile
  printf,1, compy, format='(1F)'
  CLOSE,1
  
; ALSO! We need to correct the split-tag fluxes in the timeseries data. Let's use this scaling array to do that too.
  
  splitdir = '/astro/ullyses/timeseries/nuv/x1dfiles/'
  
  for j = 1,2 do begin 
    splitdata = mrdfits(splitdir+'split_'+bad(i)+'_'+STRTRIM(j,1)+'_x1d.fits',1,h3,/SILENT)
    newflux = splitdata[1].flux/compy
    splitdata[1].flux = newflux
    mwrfits,splitdata,outdir+'split_'+bad(i)+'_'+STRTRIM(j,1)+'_x1d_newflux.fits',h3,/create
  endfor
  
  print,'Finished with '+bad(i)
  
endfor


end