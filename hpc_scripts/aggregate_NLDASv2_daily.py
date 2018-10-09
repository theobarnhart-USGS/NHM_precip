import pandas as pd
import geopandas as gpd
import numpy as np
import glob as glob
import rasterio as rs
import sys
import os.path
import datetime

reg = sys.argv[1]
#reg = '02' # for testing

def fix_length(x,y,percents):
    '''
    add the percents to the lists of index values
    '''
    xnew = []
    ynew = []
    percentsnew = []
    for xx,yy,pp in zip(x,y,percents):
        if (len(xx) > 0) and (len(yy) > 0):
            xnew.append(xx)
            ynew.append(yy)
            percentsnew.append(pp)
    return xnew,ynew,percentsnew

def get_year(index):
    return index.year

def get_month(index):
    return index.month

def get_day(index):
    return index.day

def get_hour(index):
    return index.hour

def get_keys(df,idxraster=[]):
    '''
    Find all index raster cell index values.
    '''
    cells = df.cells
    percents = df.percents
    
    x = []
    y = []
    
    if len(cells) != 1: # if there is more than one cell for the HRU
        for cell in cells:
            xx,yy = np.where(idxraster == cell) # find x and y index positions for each index raster cell
            x.append(xx)
            y.append(yy)
    
    else: # if there is only one cell for the hru
        xx,yy = np.where(idxraster == cells[0])
        x.append(xx)
        y.append(yy)

    x,y,percents = fix_length(x,y,percents) # append the percents

    assert len(x) == len(y),'Index Lengths Unequal'
    
    return x,y,percents

## generate the time aspect of the data
# the Livneh data start at 1915 and end 2015

dates = pd.date_range(start = '1979-01-02', end = '2017-12-31', freq = 'D')
#months = pd.date_range(start = '1915-01', end = '2015-12', freq = 'M')

with rs.open('../data/NLDASv2_idx_125.tiff') as ds:
    idxRast = np.flipud(ds.read(1)) # flip this to deal with the change from tiff to array

dat = pd.read_pickle('../data/NLDASv2_huc_%s_cell_contrib.pcl'%reg)

# get the index values of each cell
res = dat.apply(get_keys,axis=1,idxraster=idxRast)
x,y,percents = zip(*res)
dat['x'] = x
dat['y'] = y
dat['percents'] = percents

# now compute some min and max index values and subset the index raster
xs = []
ys = []
for x,y in zip(dat.x,dat.y):
    xs.extend(x)
    ys.extend(y)

xs = np.unique(xs)
ys = np.unique(ys)

# get extents on the local data set needed
minX = xs.min()
maxX = xs.max()
minY = ys.min()
maxY = ys.max()

extents = [minX,maxX,minY,maxY]

idxLocal = idxRast[minX:maxX,minY:maxY] # subset the index raster

r,t = idxLocal.shape

res = dat.apply(get_keys,axis=1,idxraster = idxLocal) # recompute local indices to subset the data stack.

x,y,percents = zip(*res)

dat['x_local'] = x
dat['y_local'] = y
dat['percents'] = percents

def get_fractional_date(fl): # update for livneh
    yearMonthDay = fl.split('.')[-5].split('A')[-1]

    year = int(yearMonthDay[:4])
    month = int(yearMonthDay[4:6])
    day = int(yearMonthDay[6:])

    dt = datetime.datetime(year,month,day)

    doy = float(dt.strftime('%j'))

    fracYear = doy/366. # compute fractional year

    return float(year) + fracYear # return year plus the fraction of the year

# check if the livneh data has already been gathered
gatheredDatFL = '/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_regional/region_%s_daily.npz'%reg
outfl = '/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_regional/region_%s_daily.npz'%reg
if os.path.isfile(gatheredDatFL) == False: 
# create and sort a data frame to ensure that files are read in the correct order.
	livneh = pd.DataFrame()
	livneh['files'] = glob.glob('/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_TP_daily/*.tiff')
	livneh['date'] = livneh.files.map(get_fractional_date)
	livneh.sort_values('date',inplace=True,ascending=True)
	livneh.reset_index()
	lenDays = len(dates)
    
	# preallocate the arrays
	Tmin = np.ndarray((lenDays,r,t),dtype=np.float16)
	Tmax = Tmin.copy()
    Prec = Tmin.copy()
    
	ct2 = 0
	ct = 0 # indexer for axis 0
	for fl in livneh.files:
	    ds = rs.open(fl)

        # get bands from NLDAS_hour2day.py
	    Tmin[ct,:,:] =np.array(ds.read(1)[minX:maxX,minY:maxY],dtype=np.float16)
	    Tmax[ct,:,:] =np.array(ds.read(2)[minX:maxX,minY:maxY],dtype=np.float16)
        Prec[ct,:,:] = np.array(ds.read(4)[minX:maxX,minY:maxY],dtype=np.float16)
	    ct += 1 # increment the counter
	    ct2 += 1 # increment 2nd counter

	    if ct2 == 100:
	    	print(fl)
	    	ct2 = 0
	    #print(fl)
	    
	noData = 9999

	# handle no data values:
	Tmin[Tmin == noData] = np.NaN
    Tmax[Tmax == noData] = np.NaN
 	Prec[Prec == noData] = np.NaN

	print('Data Gather Complete.')

	np.savez(outfl,Tmin=Tmin,Tmax=Tmax,Prec=Prec)
	print('Saving NLDASv2 Regional Data')

else:
	print('Loading NLDASv2 Regional Data')
	inDat = np.load(outfl)
	Tmin = inDat['Tmin']
    Tmax = inDat['Tmax']
	Prec = inDat['Prec']
    del inDat # clean up

print('Length of gathered data: %s'%len(Prec))
# now loop through each nhru in the region
# prepair the output data frame
out = pd.DataFrame()
out['datetime'] = dates
out.index = pd.DatetimeIndex(out.datetime)
out['year'] = out.index.map(get_year)
out['month'] = out.index.map(get_month)
out['day'] = out.index.map(get_day)
out['hour'] = 0
out['minute'] = 0
out['second'] = 0
#print('Length of output DataFrame: %s'%len(out))

for hru in dat.hru_id_reg: # create space for each HRU
    out['hru_%s'%hru] = -999
    
del out['datetime'] # clean up

Pout = out.copy()
del out
Tminout = Pout.copy()
Tmaxout = Pout.copy()
numHRU = float(len(dat))

# fix index lists with blank 

print('Preallocate Complete.')
print('Length of preallocated DataFrame: %s'%len(Tminout))
ct = 0
ct2 = 0
# iterate through each hru and process the whole stack!
for hru,x,y,percents in zip(dat.hru_id_reg,dat.x_local,dat.y_local,dat.percents):
    #print('%s,%s'%(len(x),len(y)))
    PrecTmp = Prec[:,x,y] # pull out the subsets from each grid
    TminTmp = Tmin[:,x,y]
    TmaxTmp = Tmax[:,x,y]

    try:
        n,m,k = PrecTmp.shape
        percents = np.reshape(percents,(1,m,k))
        percents = np.repeat(percents,n,axis=0)
        
        PrecTmp = np.nansum(PrecTmp * percents,axis=1)
        TminTmp = np.nansum(TminTmp * percents,axis=1)
        TmaxTmp = np.nansum(TmaxTmp * percents,axis=1)
        #print('Shape of processed data: %s,%s'%PrecTmp.shape)
        #convert units
        Pout['hru_%s'%hru] = PrecTmp * 0.0393701 # mm >> inches
        Tminout['hru_%s'%hru] = (TminTmp * (9./5.)) + 32 # deg C >> Deg F
        Tmaxout['hru_%s'%hru] = (TmaxTmp * (9./5.)) + 32 # deg C >> Deg F
    except:
        print('HRU %s Error.'%hru)

    if ct2 == 100:
        print('Completed %s percent'%(round((ct/numHRU)*100.,2)))
        ct2 = 0

    ct += 1
    ct2 += 1

# save the data
Pout.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_P_daily_reg_%s.pcl'%reg)
Tminout.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_Tmin_daily_reg_%s.pcl'%reg)
Tmaxout.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_Tmax_daily_reg_%s.pcl'%reg)