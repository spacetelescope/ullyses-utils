pro vignette_correct

;hi! we're comparing these two datasets to adjust the continuum for a spectrum that exhibits vignetting. 

dir = '~/functional/ullyses/tw_hydra/'

normdata = 'le9d1cdgq_x1d' ;normal dataset
vigndata = 'le9d1cdeq_x1d' ;vignetted dataset

dat1 = mrdfits(dir+normdata+'.fits',1,h1)  
dat2 = mrdfits(dir+vigndata+'.fits',1,h2)  

;let's take everything out and look at it

flux1 = [dat1[0].flux,dat1[1].flux,dat1[2].flux] ; get Strip A/B/C fluxes from normal dataset 
wave1 = [dat1[0].wavelength,dat1[1].wavelength,dat1[2].wavelength] ; " " wavelengths " " 

flux2 = [dat2[0].flux,dat2[1].flux,dat2[2].flux] ; get Strip A/B/C fluxes from vignetted dataset 
wave2 = [dat2[0].wavelength,dat2[1].wavelength,dat2[2].wavelength] ; " " wavelengths " " 

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

;we want to fit lines to the continuum fluxes, 'coeff' gives yfits to plot the lines

coeff1 = poly_fit(wavecont1,fluxcont1,1,yfit = fit1)
coeff2 = poly_fit(wavecont2,fluxcont2,1,yfit = fit2)

;here's a window that shows the normal & vignetted data (blue / red) and the selected continuum in the vignetted data
window,0

cgplot,wave1,flux1,color = 'blue', yrange = [0,8e-13],xrange = [2750,2900]
cgplot,wave2+0.5,flux2/0.92,color = 'red',/overplot
cgplot,wavecont2+0.5,fluxcont2,thick=2,/overplot

;here's a window that shows the slopes of the continuua in from each dataset, the vignetted data is fainter at short wavelengths
window,1

cgplot,wavecont2,fit2,thick = 2,color = 'red',xrange = [2750,2900], yrange = [1e-14,5e-14], title = 'Uncorrected'; vignetted data
cgplot,wavecont1,fit1,thick = 2,/overplot,color = 'blue' ; normal data

cgplot,wave1,flux1,color = 'blue',/overplot ;continuum fit to normal data
cgplot,dat2[1].wavelength+0.5,dat2[1].flux,color = 'red',/overplot ;continuum fit to *Strip B* of the vignetted data

; let's fit a line to the ratio between the continuum fluxes from both datasets

result = linfit(wavecont2,fit2/fit1) ; this gives the slope

compy = result(1)*dat2[1].wavelength + result(0) ; this gives us the y-value of the line across the *Strip B* wavelengths

ok = where(compy gt 1.,count) ; the ratio goes *over* 1.0 at longer wavelengths, let's find those array values

compy(ok) = 1. ; aaaaand make them equal to 1.0, now only the vignetted portion of the spectrum will be scaled

; here's a similar distribution to Window 1, except the vignetted flux is corrected on the short wavelength side
window,2

cgplot,wave1,flux1,color = 'blue',xrange = [2750,2900], yrange = [1e-14,5e-14], title = 'Corrected'
cgplot,dat2[1].wavelength+0.5,dat2[1].flux/compy,color = 'red',/overplot

; This distribution looks good, let's define it as the new flux for Strip B of this vignetted dataset 

newflux = dat2[1].flux/compy
dat2[1].flux = newflux

mwrfits,dat2,dir+vigndata+'_newflux.fits',h2,/create ; and then save the updated vignetted dataset as a new file


end