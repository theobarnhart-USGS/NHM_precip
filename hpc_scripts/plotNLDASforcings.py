import matplotlib
matplotlib.use('Agg')
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt

reg = sys.argv[1] # region, first argument on the command line
outs  = []
noDataCounts = []
for var in ['Tmin','Tmax','P']:
	fl = '../data/NLDASv2_%s_daily_reg_%s.pcl'%(var,reg)
	dat = pd.read_pickle(fl) # load the data
	
	for hru in dat.columns: # make no data values NaNs
		dat.loc[dat[hru] == -999,hru] = np.NaN

	noDataCounts.append(dat.isnull().sum().sum()) # count no data values

	dat = dat = dat.groupby('year').mean() # compute annual averages
	dat = dat.values[:,5:] # subset out only the data, not the indexing
	outs.append(dat) # append to object

# make the plot

p = plt.figure(figsize=(10,5))
p1 = p.add_subplot(311)
tmp = p1.pcolormesh(outs[0])
plt.colorbar(tmp,label='Tmin')

p2 = p.add_subplot(312)
tmp = p2.pcolormesh(outs[1])
plt.colorbar(tmp,label='Tmax')
p2.set_ylabel('Year from 1979')

p3 = p.add_subplot(313)
tmp = p3.pcolormesh(outs[2])
plt.colorbar(tmp,label='P')
p3.set_xlabel('HRU')

p1.set_title('Region %s NoData Values: Tmin - %s, Tmax - %s, P - %s'%(str(reg),noDataCounts[0],noDataCounts[1],noDataCounts[2]), fontsize=14)

outfl = '../data/NLDASv2_figs/NLDASv2_region_%s.png'%(reg)
p.tight_layout()
plt.savefig(outfl, bbox_in = 'tight', dpi = 300)
