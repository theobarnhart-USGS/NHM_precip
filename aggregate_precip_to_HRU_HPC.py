import pandas as pd
import numpy as np
import rasterio as rs
import geopandas as gpd
from netCDF4 import Dataset
import os
import datetime
import sys

reg = sys.argv[1] # pull the argument passed to the script

fl = '../nhru_%s_clean.shp'%reg # shapefile

def process_tiffs(df):
    reg = df.reg
    nhru = df.nhruID
    
    fl = '../HUC_%s_nhruID_%s.tiff'%(reg,nhru) # path to the tiffs
    
    if os.path.isfile(fl): # only proceed if the tiff exists
        with rs.open(fl) as ds:
            rast = ds.read(1)

        n,m = rast.shape
        rast.shape = n*m
        rast = rast[rast!=0] # remove no data cells
        k = float(len(rast))

        cells = np.unique(rast)
        #print(len(cells))
        percents = []
        for cell in cells:
            percents.append(len(rast[rast==cell])/k) # divide by the total cells in the basin to get the propotion of each cell in the basin

        cells = list(cells)
        return cells,percents
    
    else:
        return [],[]


def compute_contributions(fl,test=False):
    tmp = gpd.read_file(fl)
    dat = pd.DataFrame() # first generate a list of hrus and their grid cell contributions
    dat['nhruID'] = tmp.hru_id_nat
    dat['reg_hruID'] = tmp.hru_id_reg
    reg = fl.split('_')[-2]
    dat['reg'] = tmp.region
    cells,percents = zip(*dat.apply(process_tiffs,axis=1)) # run the aggregation function
    dat['cells'] = cells # insert results back into the dataframe
    dat['percents'] = percents

    if (reg == '08') | (reg == '10U') | (reg == '04'): # if either of these regions occur
        dat2 = pd.read_pickle('/home/tbarnhart/projects/NHM_precipitation/data/reg%s_unclipped.pcl'%reg) # load the missing data
        
        for nhru in dat2.nhruID: # remove the overlapping rows from the data frame
            dat = dat[dat.nhruID != nhru]
        
        dat = dat.append(dat2) # merge the two dataframes
    
    # write some tests
    if test:
        # do all the percentages equal very close to 1
        def test_percent(df):
            perc = np.sum(df.percents)
            if 1-perc > 0.0001:
                print('percent does not sum: %s: %s'%(1-perc,df.nhruID))
            
        dat.apply(test_percent,axis=1)
        # is the length of the original df the same as the produced one
        if len(tmp) - len(dat) > 0:
            print('data frames are different lengths')
    
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

def year(index): return index.year
def month(index): return index.month
def day(index): return index.day

def compute_precip(df,datetime=[],rast=[],out=[]):
    '''
    Compute precip for an hru based on its contributing grid cells
    '''
    
    precip = rast[df.cells]
    percents = np.array(df.percents)
    
    weighted_precip = np.sum(precip*percents) # precip in mm
    weighted_precip *= 0.0393701 # mm > inches

    out.loc[datetime,'hru_%s'%df.reg_hruID] = weighted_precip # insert into the out data frame



def generate_output(fl):
    reg = fl.split('_')[-2] # extract the region
    print('Starting region %s...'%reg)
    dat = pd.read_pickle('../huc_%s_cell_contrib.pcl'%reg) # load the contributing cells and percentages
    dat.sort_values('reg_hruID',inplace=True,ascending=True) # sort by regional hru
    
    # prepair the output data frame
    out = pd.DataFrame()
    out['datetime'] = pd.DatetimeIndex(times)
    out.index = pd.DatetimeIndex(out.datetime)
    out['year'] = out.index.map(year)
    out['month'] = out.index.map(month)
    out['day'] = out.index.map(day)
    out['hour'] = 0
    out['minute'] = 0
    out['second'] = 0

    for hru in dat.reg_hruID: # create space for each HRU
        out['hru_%s'%hru] = -999

    del out['datetime'] # clean up

    for i in range(m): # iterate through slices of the dataset
        rast = np.array(ds.variables['Total_precipitation_surface_1_Hour_Accumulation'][i,:,:]) # pull a slice
        rast.shape = (k*l) # reshape the dataset in the say way as the index values
        print('Starting: %s'%(times[i])) #print 
        dat.apply(compute_precip,axis=1,datetime=times[i],rast=rast,out=out) # compute precip for each hru for the time slice
        print('Completed: %s'%(times[i]))
    
    out.to_csv('../hru_%s_stage_4_precip.cbh'%reg,sep=' ',header=False,index=False,float_format='%.2f',na_rep='-999')
    out.to_pickle('../hru_%s_stage_4_precip.pcl'%reg)
    
    print('Region %s complete!'%reg)

# run these functions
compute_contributions(fl, test=True)
generate_output(fl)
