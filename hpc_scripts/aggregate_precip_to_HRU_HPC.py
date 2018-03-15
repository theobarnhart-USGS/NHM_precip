import pandas as pd
import numpy as np
import rasterio as rs
import geopandas as gpd
from netCDF4 import Dataset
import os
import datetime
import sys
import gdal

computeContrib = False
reg = sys.argv[1] # pull the argument passed to the script
fl = '../nhru_%s_clean.shp'%reg # shapefile
idxraster = '../hrap_grid_AEA.tiff' # the index raster to use with 

def get_cell(geom,gt=[],rb=[]):
    ''' Grab index cell value for an hru that is too small to create a tiff for.
    geom = hru geometry 
    gt = geotransform
    rb = raster band to pick data from
    '''
    # grab the centrioid
    mx = geom.exterior.centroid.x
    my = geom.exterior.centroid.y
    
    # transform to array coordinates
    px = int((mx-gt[0])/gt[1]) # x pixle
    py = int((my-gt[3])/gt[5]) # y pixle
    
    # extract the value
    intval = rb.ReadAsArray(px,py,1,1)
    return intval[0][0]

def process_tiffs(df,gt=[],rb=[]):
    '''Process the tiffs or use the cell finder if the tiff does not exist
    Inputs:
    df = geopandas data frame of the cooresponding regional shapefile
    gt = geotransform
    rb = raster band
    '''
    
    fl = '../HUC_%s_hruID_%s.tiff'%(df.region,df.hru_id_reg) # path to the tiffs

    #if os.path.isfile(fl) == True: # only proceed if the tiff exists
    with rs.open(fl) as ds:
        rast = ds.read(1)

    n,m = rast.shape
    rast.shape = n*m
    rast = rast[rast!=0] # remove no data cells
    k = float(len(rast)) # this should probably be the number of cells each larger cell is divided into.

    cells = np.unique(rast)
    #print(len(cells))
    percents = []
    for cell in cells:
        percents.append(len(rast[rast==cell])/k) # divide by the total cells in the basin to get the propotion of each cell in the basin

    cells = list(cells)
    return cells,percents
    
    #elif os.path.isfile(fl) == False: # if the raster does not exist, find the grid cell that the hru centroid occupies
    #    return [get_cell(df.geometry,gt = gt,rb = rb)],[1.]

 
def compute_contributions(fl,idxraster = idxraster,test=False):
    '''Compute grid cell contributions to hrus within a region'''
    
    # load the index raster and pull the geotransformation:
    src_ds = gdal.Open(idxraster)
    gt = src_ds.GetGeoTransform()
    rb = src_ds.GetRasterBand(1)

    dat = gpd.read_file(fl)
    reg = fl.split('_')[-2]
    cells,percents = zip(*dat.apply(process_tiffs,axis=1,gt=gt,rb=rb)) # run the aggregation function
    
    dat['reg'] = reg
    
    dat['cells'] = cells # insert results back into the dataframe
    dat['percents'] = percents

    # removed because of new cell finder implementation for missing HRUS!
    #if (reg == '08') | (reg == '10U') | (reg == '04'): # if either of these regions occur
    #    dat2 = pd.read_pickle('/home/tbarnhart/projects/NHM_precipitation/data/reg%s_unclipped.pcl'%reg) # load the missing data
    #    
    #    for nhru in dat2.nhruID: # remove the overlapping rows from the data frame
    #        dat = dat[dat.nhruID != nhru]
    #    
    #   dat = dat.append(dat2) # merge the two dataframes
    
    # write some tests
    if test:
        # do all the percentages equal very close to 1
        def test_percent(df):
            perc = np.sum(df.percents)
            if 1-perc > 0.0001:
                print('percent does not sum: %s: %s'%(1-perc,df.hru_id_reg))
            
        dat.apply(test_percent,axis=1)
        # is the length of the original df the same as the produced one
        #if len(tmp) - len(dat) > 0:
        #    print('data frames are different lengths')
    
    # remove geometry from the data frame:
    del dat['geometry']
    dat.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/nhru_contrib/huc_%s_cell_contrib.pcl'%reg)
    dat.to_pickle('../huc_%s_cell_contrib.pcl'%reg)
    print('%s Complete!'%reg)

# load the precip data
infl = '../stage4_map_daily_20041220-20150107.nc'
ds = Dataset(infl,'r')
m,k,l = ds.variables['Total_precipitation_surface_1_Hour_Accumulation'].shape # get the dimensions of the precip data

# compute the dates
time = ds.variables['time']
#print('Time Units: %s'%time.units)
timeoffset = time.units[-20:] # strip the string
strt = pd.to_datetime(timeoffset) # convert string into datetime object
time = np.array(ds.variables['time'])

def compute_time(time,offset):
    dt = datetime.timedelta(hours=time)
    time = offset+dt
    return str(time.date())

times = np.vectorize(compute_time)(time,strt)

def get_year(index):
    return index.year

def get_month(index):
    return index.month

def get_day(index):
    return index.day

def compute_precip(df,datetime=[],rast=[],out=[],PP=[]):
    '''
    Compute precip for an hru based on its contributing grid cells
    '''
    
    precip = rast[np.array(df.cells,dtype=np.int)] # pull out the cells from the hrap grid
    percents = np.array(df.percents) # create an array of the percents that each cell contributes to the hru
    
    # compute weighted average precipitation following:
    # https://github.com/theobarnhart/WSC_WRF/blob/master/extract_watershed_data_HW.ipynb
    # at commit: b06e99fdf404536af2c07766a53c3759763c9845

    weights = np.ndarray(len(percents),dtype=np.float64) # preallocate the weights matrix
    weights[:] = 1./len(percents) # fill the weights with 1/n where n is the number of cells feeding into the hru
    weights = weights * percents # change the weights to 
    weighted_precip = np.sum(precip*weights) # precip in mm, propogate NaNs

    weighted_precip *= 0.0393701 # mm >> inches

    out.loc[datetime,'hru_%s'%df.hru_id_reg] = weighted_precip # insert into the out data frame

    # compute proportion of HRU with precipitation
    precip[precip>0] = 1. # set the precip vector values based on internal values
    precip[precip<=0] = 0.

    propP = np.nansum(precip * weights) / len(percents) # compute area weighted proportion of HRU with precipitation.

    # save the precip presence data
    PP.loc[datetime,'hru_%s'%df.hru_id_reg] = propP


def generate_output(fl,contribFile=[]):
    reg = fl.split('_')[-2] # extract the region
    print('Starting region %s...'%reg)
    dat = pd.read_pickle(contribFile) # load the contributing cells and percentages
    dat.sort_values('hru_id_reg',inplace=True,ascending=True) # sort by regional hru
    
    # prepair the output data frame
    out = pd.DataFrame()
    out['datetime'] = pd.DatetimeIndex(times) # change back non-demo
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

    PP = out.copy() # make a copy of the output data frame for the precip proportion data frame

    for i in range(len(out)): # iterate through slices of the dataset
        rast = np.array(ds.variables['Total_precipitation_surface_1_Hour_Accumulation'][i,:,:]) # pull a slice
        rast.shape = (k*l) # reshape the dataset in the same way as the index values
        print('Starting: %s'%(times[i])) #print 
        dat.apply(compute_precip,axis=1,datetime=times[i],rast=rast,out=out,PP=PP) # compute precip for each hru for the time slice
        print('Completed: %s'%(times[i]))

    # output intermediate products    
    #out.to_csv('../hru_%s_stage_4_precip.cbh'%reg,sep=' ',header=False,index=False,float_format='%.2f',na_rep='-999')
    #out.to_pickle('../hru_%s_stage_4_precip.pcl'%reg)
    
    #PP.to_csv('../hru_%s_stage_4_precip_prop.cbh'%reg,sep=' ',header=False,index=False,float_format='%.2f',na_rep='-999')
    #PP.to_pickle('../hru_%s_stage_4_precip_prop.pcl'%reg)

    # interpolate the precipitation forcings
    
    # generate lists of dates
    strt = str(out.index[0])
    nd = str(out.index[-1])
    dt = datetime.timedelta(1)

    dates = []
    [dates.append(str(date)) for date in pd.date_range(strt,nd,freq='D')]

    dsDates = []
    [dsDates.append(str(date)) for date in out.index]
    
    missing = list(set(dates) - set(dsDates)) # compute the difference between the two lists

    if len(missing) == 0:
        print('Dates match, no interpolation needed')
    else:
        print('Dates missing, interpolation needed')

        for date in missing: # iterate through the missing dates
            print(date)
            # find the dates before and after the missing date
            year = int(date.split(' ')[-2].split('-')[0])
            month = int(date.split(' ')[-2].split('-')[1])
            day = int(date.split(' ')[-2].split('-')[2])
            date = datetime.date(year,month,day)
            before = date - dt
            after = date + dt

            out2 = pd.DataFrame()
            out2['datetime'] = [date]
            out2['year'] = year
            out2['month'] = month
            out2['day'] = day
            out2['hour'] = 0
            out2['minute'] = 0
            out2['second'] = 0

            # iterate through each HRU
            for hru in out.columns[6:]:
                out2[hru] =((out.loc[out.index==str(before),hru].as_matrix() + out.loc[out.index==str(after),hru].as_matrix()) / 2.)[0]

            out2.index = pd.DatetimeIndex(out2.datetime)
            del out2['datetime']
            out = out.append(out2)

    out.sort_index(inplace=True)
    #out.interpolate(limit=5,inplace=True)

    print('Region: %s interpolation complete'%reg)
    
    # save the output
    out.to_csv('../hru_%s_stage_4_precip.cbh'%reg,sep=' ',header=False,index=False,float_format='%.2f',na_rep='-999')
    out.to_pickle('../hru_%s_stage_4_precip.pcl'%reg)
    
    PP.to_csv('../hru_%s_stage_4_precip_prop.cbh'%reg,sep=' ',header=False,index=False,float_format='%.2f',na_rep='-999')
    PP.to_pickle('../hru_%s_stage_4_precip_prop.pcl'%reg)

    print('Region %s complete!'%reg)

# run these functions

contribFile = '/home/tbarnhart/projects/NHM_precipitation/data/nhru_contrib/huc_%s_cell_contrib.pcl'%reg

if (os.path.isfile(contribFile) == False) | (computeContrib == True): # check if the HRU contributions have already occured
    print('Computing contributions to HRUS...')
    compute_contributions(fl, test=True)
    contribFile = '../huc_%s_cell_contrib.pcl'%reg
else:
    print('Contributions to HRUS previously computed!')

generate_output(fl, contribFile=contribFile)