# ## Script to clip the index raster to each NHM HRU
# 
# Theodore Barnhart | tbarnhart@usgs.gov
#########################################

import geopandas as gpd
import subprocess
import os
import numpy as np
import pandas as pd
import sys

reg = sys.argv[1] # extract the region from the wrapper function


def make_outpath(df):
    outpath = '~/projects/NHM_precipitation/data/spherical_tiffs/HUC_%s_hruID_%s.tiff'%(df.region,df.hruID)
    return outpath

def clip_raster(df):
    
    cutline = df.cutline
    feature = df.hruID
    inpath = df.inpath
    outpath = df.outpath
    
    cmd = "gdalwarp -tr 0.0125 0.0125 -cutline %s -cwhere hru_id_reg=%s -crop_to_cutline -overwrite %s %s"%(cutline,
        feature,inpath,outpath)
    
    subprocess.call(cmd,shell=True)
    
    return None


def runClip(fl,inpath='tmp'):
    tmp = gpd.read_file(fl)
    dat = pd.DataFrame({'hruID':tmp.hru_id_reg.unique()}) #dataframe of the unique NHM HRU identifiers
    del tmp # close tmp file
    
    reg = fl.split('_')[-2] # extract the region
    
    dat['cutline'] = fl # insert the shapefile as the cutline
    dat['region'] = reg
    dat['inpath'] = inpath # specified
    dat['outpath'] = dat.apply(make_outpath,axis=1)
    
    dat.apply(clip_raster,axis=1) # run the clip code
    print('HUC%s Done!'%reg)
    return None

def is_file(df):
    hru = df.hruID
    reg = df.region
    return os.path.isfile('./AEA_tiffs/HUC_%s_hruID_%s.tiff'%(reg,hru))

def parse_out(out):
    out = str(out.stdout)
    x = int(out.split()[-1].split('L')[0])
    y = int(out.split()[-3].split('P')[0])
    return x,y

def clip_raster_output(df):
    '''Save the output from the gdal command to see what the error was.'''

    cutline = df.cutline
    feature = df.hruID
    inpath = df.inpath
    outpath = df.outpath
    
    cmd = "gdalwarp -tr 0.0125 0.0125 -cutline %s -cwhere hru_id_reg=%s -crop_to_cutline -overwrite %s %s"%(cutline,
        feature,inpath,outpath)
    
    out = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE)
    
    return out


def check(fl,inpath='tmp'):
    '''Figure out which HRUS are missing'''
    reg = fl.split('_')[-2] # extract the region
    tmp = gpd.read_file(fl)
    dat = pd.DataFrame({'hruID':tmp.hru_id_reg.unique()}) #dataframe of the unique NHM HRU identifiers
    del tmp # close tmp file
    
    dat['cutline'] = fl # insert the shapefile as the cutline
    dat['region'] = reg
    dat['inpath'] = inpath # specified
    dat['outpath'] = dat.apply(make_outpath,axis=1)
    dat['region'] = reg # insert the region
    dat['isfile'] = dat.apply(is_file,axis=1)
    
    dat2 = dat.loc[dat.isfile==False].copy() # select only the missing files
    
    if len(dat2) > 0:
        dat2['out'] = dat2.apply(clip_raster_output,axis=1) # run the clip routine again, but save the output
        res = dat2.out.map(parse_out) # parse the output into the raster size trying to be created
        x,y = zip(*res) # unpack the results and put into the dataframe 
        dat2['cols'] = x
        dat2['rows'] = y
        dat2['cells'] = dat2.rows*dat2.cols
    
        if dat2.cells.sum()>0:
            print('non-zero raster!')
    
        return dat2
    
    elif len(dat) - dat.isfile.sum() == 0:
        print('%s Complete!'%reg)

# now that all the functions are written...
fl = '/home/tbarnhart/projects/NHM_precipitation/data/nhru_%s_clean.shp'%reg
inpath = '~/projects/NHM_precipitation/data/NLDASv2_idx_0125.tiff'
runClip(fl,inpath=inpath) # crop the files
missing = check(fl,inpath=inpath) # figure out whats missing
missing.to_pickle('/home/tbarnhart/projects/NHM_precipitation/data/missing_NLDASv2_clip_region_%s.pcl'%reg) # save the file

#files = glob.glob('~/projects/NHM_precipitation/data/nhrus/clean_AEA/*.shp') # load the files
#files = pd.DataFrame({'file':files})

# clip the rasters
#files.file.apply(runClip,inpath='./hrap_grid_AEA_idx_sm.img')
#missing = files.file.apply(check,inpath='./hrap_grid_AEA_idx_sm.img')

# region 4
#reg04_NHRU = [17305,20935,21024,21727,22256]
#reg04_cells = [[296823],[354989],[356077],[306739],[260807]]
#reg04_percents = [[1],[1],[1],[1],[1]]
#reg04 = pd.DataFrame()
#reg04['nhruID'] = reg04_NHRU
#reg04['reg_hruID'] = [117,3747,3836,4539,5068]
#reg04['cells'] = reg04_cells
#reg04['percents'] = reg04_percents
#reg04['reg'] = '04'
#reg04.to_pickle('~/projects/NHM_precipitation/data/reg04_unclipped.pcl')

# region 8
#reg08_NHRU = [40817,40910,40926,40826,40827,40891,40908,41064]
#reg08_cells = [[788822],[780963],[772030],[778776],[778776],[776509],[780963],[760827]]
#reg08_percents = [[1],[1],[1],[1],[1],[1],[1],[1]]
#reg08 = pd.DataFrame()
#reg08['nhruID'] = reg08_NHRU
#reg08['reg_hruID'] = [3,96,112,12,13,77,94,250]
#reg08['cells'] = reg08_cells
#reg08['percents'] = reg08_percents
#reg08['reg'] = '08'
#reg08.to_pickle('~/projects/NHM_precipitation/data/reg08_unclipped.pcl')

# region 10 upper
#reg10U_NHRU = [63665,63681]
#reg10U_cells = [[354526],[354513]]
#reg10U_percents = [[1],[1]]
#reg10U = pd.DataFrame()
#reg10U['nhruID'] = reg10U_NHRU
#reg10U['reg_hruID'] = [8082,8098]
#reg10U['cells'] = reg10U_cells
#reg10U['percents'] = reg10U_percents
#reg10U['reg'] = '10U'
#reg10U.to_pickle('~/projects/NHM_precipitation/data/reg10U_unclipped.pcl')
