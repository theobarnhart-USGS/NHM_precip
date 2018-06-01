# Script to move files and then run the aggregation script
# Theodore Barnhart | tbarnhart@usgs.gov
# 20171106

reg=$1 # parse the first argument passed to the wrapper

# move files to the node:
cp ~/projects/NHM_precipitation/data/stage4_map_daily_20041220-20150107.nc $GLOBAL_SCRATCH/ # move the precip data

#cp ~/projects/NHM_precipitation/data/AEA_tiffs/HUC_${reg}_nhruID_*.tiff $GLOBAL_SCRATCH/ # move the tiffs needed

cp ~/projects/NHM_precipitation/data/nhru_${reg}_clean.* $GLOBAL_SCRATCH/ # move the shapefile

mkdir $GLOBAL_SCRATCH/work
cd $GLOBAL_SCRATCH/work # move to the working directory

# setup the working environment
module load python/anaconda3
source activate py36 

# call the script and pass the region argument
python ~/projects/NHM_precipitation/aggregate_precip_to_HRU_HPC.py $reg

# move some files back to the home directory
cp ../hru_${reg}_stage_4_precip.cbh ~/projects/NHM_precipitation/data/
cp ../hru_${reg}_stage_4_precip.pcl ~/projects/NHM_precipitation/data/

# once finished, clean up
#rm ../HUC_${reg}_nhruID_*.tiff
