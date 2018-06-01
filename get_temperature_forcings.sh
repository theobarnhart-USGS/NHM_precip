cd ./data
#mkdir forcing_sets
cd forcing_sets
#mkdir daymet

#scp -l 3200 yeti:/cxfs/projects/usgs/water/mows/NHM/bandit/daymet/*tmax*.gz ./daymet/
#scp -l 3200 yeti:/cxfs/projects/usgs/water/mows/NHM/bandit/daymet/*tmin*.gz ./daymet/

#mkdir maurer

#scp -l 3200 yeti:/cxfs/projects/usgs/water/mows/NHM/bandit/maurer/*tmax*.gz ./maurer/
#scp -l 3200 yeti:/cxfs/projects/usgs/water/mows/NHM/bandit/maurer/*tmin*.gz ./maurer/

#mkdir idaho

#scp -l 3200 yeti:/cxfs/projects/usgs/water/mows/NHM/bandit/idaho/*tmax*.gz ./idaho/
#scp -l 3200 yeti:/cxfs/projects/usgs/water/mows/NHM/bandit/idaho/*tmin*.gz ./idaho/

#mkdir livneh

scp -l 3200 yeti:/cxfs/projects/usgs/water/wymtwsc/tbarnhart/projects/NHM_precipitation/transfer/livneh2016/*Tmax*.zip ./livneh/
scp -l 3200 yeti:/cxfs/projects/usgs/water/wymtwsc/tbarnhart/projects/NHM_precipitation/transfer/livneh2016/*Tmin*.zip ./livneh/
