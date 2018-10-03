import rasterio as rs
import numpy as np
import datetime
import os

def convert(date):
    '''
    Function to convert hourly NLDAS tiffs to daily summaries from midnight to 11 pm.
    '''
    outfl = './data/NLDASv2_TP_daily/LDAS_FORA0125_H.A%s.002.grb.TP.tiff'%(date.strftime('%Y%m%d'))
    
    if not os.path.isfile(outfl):

        # preallocate T and P grids
        T = np.zeros((24,224,464),dtype=np.float32)
        T[:] = np.NaN
        P = T.copy()

        for hr in range(0,24): # create daily data cube.
            fl = './data/NLDASv2/NLDAS_FORA0125_H.A%s.%s00.002.grb.TP.tiff'%(date.strftime('%Y%m%d'),str(hr).zfill(2))
            #print(fl)
            with rs.open(fl) as ds:
                T[hr,:,:] = ds.read(1)
                P[hr,:,:] = ds.read(2)
                if hr == 23:
                    profile = ds.profile
                    noData = ds.nodata
        
        # update geoTiff profile with creation options, new band count, etc.            
        profile.update({'compress':'LZW',
                    'profile':'GeoTIFF',
                    'tiled':True,
                    'sparse_ok':True,
                    'num_threads':'ALL_CPUS',
                       'nodata':9999,
                       'dtype':'float32',
                       'count':4})

        T[T==noData] = np.NaN
        P[P==noData] = np.NaN

        # summarize data cubes
        Tmin = np.nanmin(T,axis=0)
        Tmax = np.nanmax(T,axis=0)
        Tave = np.nanmean(T,axis=0)
        Ptot = np.nansum(P,axis=0)

        # write out the summarized geoTiff
        with rs.open(outfl,'w',**profile) as dst:
            dst.write(Tmin,1)
            dst.write(Tmax,2)
            dst.write(Tave,3)
            dst.write(Ptot,4)

        print('%s Processed'%(date.strftime('%Y-%m-%d')))

    else: print('%s Already Processed'%(date.strftime('%Y-%m-%d'))) 

    return None

def daterange(strtDate,endDate,fmt):
    '''
    strtDate = start date (string)
    endDate = end date (string)
    fmt = format to parse input strings with
    '''
    strtDate = datetime.datetime.strptime(strtDate,fmt)
    endDate = datetime.datetime.strptime(endDate,fmt)

    step = datetime.datetime.timedelta(days=1)

    dates = []

    while strtDate <=endDate:
        dates.append(strtDate)
        strtDate += step

    return dates

# create list of dates to convert
fmt = '%Y-%m-%d'
strtDate = '1979-01-02'
endDate = '2017-12-31'

dates = daterange(strtDate,endDate,fmt)

for date in dates:
    convert(date)