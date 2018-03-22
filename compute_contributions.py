import pandas as pd
import numpy as np
import rasterio as rs
import geopandas as gpd
from netCDF4 import Dataset
import os
import datetime
import sys
import gdal

reg = sys.argv[1] # pull the argument passed to the script
fl = './data/nhrus/clean_AEA/nhru_%s_clean.shp'%reg # shapefile
idxraster = './data/livneh_idx_laea.tiff' # the index raster to use with

def get_cell(geom,gt=[],rb=[]):
    ''' Grab index cell value for an hru that is too small to create a tiff for.
    geom = hru geometry 
    gt = geotransform
    rb = raster band to pick data from
    '''
    # grab the centrioid
    mx = geom.centroid.x
    my = geom.centroid.y
    
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
    
    fl = './data/nhrus/AEA_tiffs/livneh_HUC_%s_nhruID_%s.tiff'%(df.region,df.hru_id_nat) # path to the tiffs

    if os.path.isfile(fl) == True: # only proceed if the tiff exists
        with rs.open(fl) as ds:
            rast = ds.read(1)

        n,m = rast.shape
        rast.shape = n*m
        rast = rast[rast!=0] # remove no data cells
        k = 100 # number of smaller cells in each index cell

        cells = np.unique(rast)
        #print(len(cells))
        percents = []
        for cell in cells:
            percents.append(len(rast[rast==cell])/k) # divide by the total cells in the basin to get the propotion of each cell in the basin

        cells = list(cells)
        return cells,percents
    
    elif os.path.isfile(fl) == False: # if the raster does not exist, find the grid cell that the hru centroid occupies
        print('W - National HRU %s tiff missing, finding index value at centroid'%df.hru_id_nat)
        return [get_cell(df.geometry,gt = gt,rb = rb)],[1.]

def compute_contributions(fl,idxraster = idxraster):
    '''Compute grid cell contributions to hrus within a region'''
    
    reg = fl.split('_')[-2] # extract region
    print('S - Starting Region: %s!'%reg)
    print('S - Using input shapefile: %s'%fl)
    print('S - Using index raster: %s'%idxraster)
    
    # load the index raster and pull the geotransformation:
    src_ds = gdal.Open(idxraster)
    gt = src_ds.GetGeoTransform()
    rb = src_ds.GetRasterBand(1)

    dat = gpd.read_file(fl)
    
    cells,percents = zip(*dat.apply(process_tiffs,axis=1,gt=gt,rb=rb)) # run the aggregation function
    
    dat['reg'] = reg
    
    dat['cells'] = cells # insert results back into the dataframe
    dat['percents'] = percents
    
    # remove geometry from the data frame:
    del dat['geometry']
    outputFile = './data/livneh_huc_%s_cell_contrib.pcl'%reg
    print('S - Writing contribution data to: %s'%outputFile)
    dat.to_pickle(outputFile)
    print('S - Region %s Complete!'%reg)
    
compute_contributions(fl)