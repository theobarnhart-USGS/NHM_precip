
import pandas as pd
import geopandas as gpd
import numpy as np
import glob as glob
from netCDF4 import Dataset
import rasterio as rs
import sys

reg = sys.argv[1]

def get_year(index):
    return index.year

def get_month(index):
    return index.month

def get_day(index):
    return index.day

def get_keys(df,idxraster=[]):
    '''
    Find index raster cell index values.
    '''
    cells = df.cells
    
    x = []
    y = []
    
    if len(cells) != 1:
        for cell in cells:
            xx,yy = np.where(idxraster == cell)
            x.append(xx)
            y.append(yy)
    
    else:
        xx,yy = np.where(idxraster == cells[0])
        x.append(xx)
        y.append(yy)
    
    return x,y

## generate the time aspect of the data
# the Livneh data start at 1915 and end 2015

dates = pd.date_range(start = '1915-01-01', end = '2015-12-31', freq = 'D')
#months = pd.date_range(start = '1915-01', end = '2015-12', freq = 'M')

with rs.open('../data/livneh_idx.tiff') as ds:
    idxRast = np.flipud(ds.read(1)) # flip this to deal with the change from tiff to array

dat = pd.read_pickle('../data/livneh_huc_%s_cell_contrib.pcl'%reg)

# get the index values of each cell
res = dat.apply(get_keys,axis=1,idxraster=idxRast)
x,y = zip(*res)
dat['x'] = x
dat['y'] = y

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

res = dat.apply(get_keys,axis=1,idxraster = idxLocal) # recompute local indices to subset the data stack.

x,y = zip(*res)

dat['x_local'] = x
dat['y_local'] = y

def get_fractional_date(fl):
    yearMonth = fl.split('.')[-2]
    year = float(yearMonth[0:4])
    month = float(yearMonth[4:6])-0.5
    
    return year + (month/12.)

# create and sort a data frame to ensure that files are read in the correct order.
livneh = pd.DataFrame()
livneh['files'] = glob.glob('/home/tbarnhart/projects/NHM_precipitation/data/livneh2016/*.nc')
livneh['date'] = livneh.files.map(get_fractional_date)
livneh.sort_values('date',inplace=True,ascending=True)

livneh.reset_index()
fl = livneh.files[0]
liv = Dataset(fl)
Tmin = np.array(liv.variables['Tmin'][:,minX:maxX,minY:maxY],dtype=np.float64)
Tmax = np.array(liv.variables['Tmax'][:,minX:maxX,minY:maxY],dtype=np.float64)
Prec = np.array(liv.variables['Prec'][:,minX:maxX,minY:maxY],dtype=np.float64)

for fl in livneh.files[1:]:
    liv = Dataset(fl)
    Tmin = np.concatenate((Tmin,np.array(liv.variables['Tmin'][:,minX:maxX,minY:maxY],dtype=np.float64)),axis=0)
    Tmax = np.concatenate((Tmax,np.array(liv.variables['Tmax'][:,minX:maxX,minY:maxY],dtype=np.float64)),axis=0)
    Prec = np.concatenate((Prec,np.array(liv.variables['Prec'][:,minX:maxX,minY:maxY],dtype=np.float64)),axis=0)
    
noData = 1e+20

# handle no data values:
Tmin[Tmin == noData] = np.NaN
Tmax[Tmax == noData] = np.NaN
Prec[Prec == noData] = np.NaN

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

for hru in dat.hru_id_reg: # create space for each HRU
    out['hru_%s'%hru] = -999
    
del out['datetime'] # clean up

Pout = out.copy()
Tminout = out.copy()
Tmaxout = out.copy()
numHRU = float(len(dat))

for hru,x,y,percents in zip(dat.hru_id_reg,dat.x_local,dat.y_local,dat.percents):
    PrecTmp = Prec[:,x,y]
    TminTmp = Tmin[:,x,y]
    TmaxTmp = Tmax[:,x,y]
    
    n,m,k = PrecTmp.shape
    percents = np.reshape(percents,(1,m,k))
    percents = np.repeat(percents,n,axis=0)
    
    PrecTmp = np.nansum(PrecTmp * percents,axis=0)
    TminTmp = np.nansum(TminTmp * percents,axis=0)
    TmaxTmp = np.nansum(TmaxTmp * percents,axis=0)
    
    #convert units
    Pout['hru_%s'%hru] = PrecTmp * 0.0393701 # mm >> inches
    Tminout['hru_%s'%hru] = (TminTmp * (9./5.)) + 32 # deg C >> Deg F
    Tmaxout['hru_%s'%hru] = (TmaxTmp * (9./5.)) + 32. # deg C >> Deg F
    print('Completed %s%'%(ct/numHRU*100.))
    ct += 1

# save the data
Pout.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/livneh_Prec_reg_%s.pcl'%reg)
Tminout.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/livneh_Tmin_reg_%s.pcl'%reg)
Tmaxout.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/livneh_Tmax_reg_%s.pcl'%reg)
