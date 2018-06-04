from objectiveFunctions import *
from temperatureComparisonFxns import *

regions = ['18', '01', '03', '08', '04', '15', '10L', '14', '05', '07', '12','11', '16', '06', '10U', '17', '02', '09', '13']
forcingTypes = ['tmin','tmax']
forcingSets = ['daymet','maurer','idaho']

for region in regions: # iterate through regions
    for forcingType in forcingTypes: # iterate through tmin and tmax
        livneh = loadDF(forcingSet='livneh',region=region,forcingType=forcingType)
        for forcingSet in forcingSets: # iterate through datasets, maurer etc.

            # load datasets
            df2 = loadDF(forcingSet=forcingSet,region=region,forcingType=forcingType)
            
            # crop to common time periods
            strt,nd = findCommomDates(datasets = [livneh,df2])
            df1 = livneh[strt:nd]
            df2 = df2[strt:nd]

            # assert that all dimensions are the same
            assert df1.shape[0] == df2.shape[0]
            assert df1.shape[1] == df2.shape[1]

            # compute 
            computeMetrics(df1,df2,label='livneh2%s'%forcingSet,forcingType=forcingType,region=region,save=True)
            
            # clean up 
            del df1
            del df2
            
    print('Region %s complete'%(region))