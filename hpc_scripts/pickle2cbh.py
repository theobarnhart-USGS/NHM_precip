import pandas as pd
import sys
import numpy as np

reg = sys.argv[1] # region, first argument on the command line
variable = sys.argv[2] # variable to convert
infl = sys.argv[3] # infile
outfl = sys.argv[4] # outfile

def pcl2cbh(infl,outfl,region,variable):
    '''convert a picle to a cbh file'''
    print('Starting %s %s'%(reg,variable))
    dat = pd.read_pickle(infl)
    
    print('%s No Data Values Found'%np.sum(np.isnan(dat.values)))
    
    fmt = '%.2f' # set output format to 2 decimal places

    if variable == 'Prec': # change the precip output to 3 decimal places
        fmt = '%.3f'
    
    dat.to_csv(outfl, sep = ' ',na_rep='-999',float_format=fmt,header=False)
    print('%s finished.'%variable)

pcl2cbh(infl,outfl,reg,variable)
