import pandas as pd
import numpy as np
import glob
from objectiveFunctions import *

def extractType(fl): return fl.split('_')[-1].split('.')[0]
def extractRegion(fl): return fl.split('/')[-1].split('_')[0].split('r')[-1]
def computeDatetime(df): return '%i-%i-%i'%(df.year,df.month,df.day)

def loadDF(forcingSet=None,region=None,forcingType=None):
    # collect data files
    files = pd.DataFrame()
    files['path'] = glob.glob('./data/forcing_sets/%s/*.cbh'%forcingSet)
    files['type'] = files.path.map(extractType)
    files['region'] = files.path.map(extractRegion)

    fl = files.loc[(files.type==forcingType) & (files.region == region)].path.values[0]
    skiprows = 3
    na_values = 'NaN'
    if forcingSet == 'Livneh':
        skiprows = 0
        na_values = [-999,'inf']
    
    dat = pd.read_table(fl,skiprows=skiprows,delim_whitespace=True,header=None, names = None,
                      low_memory=True, na_values=na_values)
    
    if forcingSet == 'Livneh':
        del dat['0'] # remove the datetime column
        
    # make column names
    n = len(dat.columns)
    header = ['year','month','day','hour','minute','second']
    for i in range(1,n+1-len(header)):
        header.append('HRU_ID_%s'%i)

    dat.columns = header
    dat['datetime'] = dat.apply(computeDatetime,axis=1)
    dat.index = pd.DatetimeIndex(dat.datetime)
    
    for var in ['year','month','day','hour','minute','second', 'datetime']: del dat[var]
        
    return dat

def computeMetrics(df1,df2,label = None, save=False, region = None, forcingType = None):
    r2res = []
    MAEres = []
    RMSEres = []
    NSEres = []
    pearsonsRres = []

    for hru in df1.columns:
        x = df1[hru].values
        y = df2[hru].values

        r2res.append(r2(x,y))
        MAEres.append(MAE(x,y))
        RMSEres.append(RMSE(x,y))
        NSEres.append(NSE(x,y))
        pearsonsRres.append(pearsonR(x,y))
        
    results = pd.DataFrame()
    results['HRU'] = np.arange(1,len(df1.columns)+1)
    results['r2'] = r2res
    results['MAE'] = MAEres
    results['RMSE'] = RMSEres
    results['NSE'] = NSEres
    results['R'] = pearsonsRres
    
    if save: results.to_pickle('./data/forcing_sets/r%s_%s_%s.pcl'%(region,forcingType,label))

def findCommomDates(datasets = []):
    starts = []
    ends = []
    for ds in datasets:
        starts.append(ds.index.min())
        ends.append(ds.index.max())

    strt = np.max(starts)
    nd = np.min(ends)
            
    return strt,nd