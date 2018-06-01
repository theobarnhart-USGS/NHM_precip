#!/bin/bash
# Script to move files and then run the aggregation script
# Theodore Barnhart | tbarnhart@usgs.gov
# 20180423
#SBATCH --job-name=aggregate_precip # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=60:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=4000            #memory in MB

reg=$1 # parse the first argument passed to the wrapper

# move files to the node:
cp ~/projects/NHM_precipitation/data/stage4_map_daily_20041220-20150107.nc $GLOBAL_SCRATCH/ # move the precip data

#cp ~/projects/NHM_precipitation/data/AEA_tiffs_regHRU/HUC_${reg}_hruID_*.tiff $GLOBAL_SCRATCH/ # move the tiffs needed

cp ~/projects/NHM_precipitation/data/nhru_${reg}_clean.* $GLOBAL_SCRATCH/ # move the shapefile

cp ~/projects/NHM_precipitation/data/hrap_grid_AEA.tiff $GLOBAL_SCRATCH/ # move the smaller hrap grid index file

mkdir $GLOBAL_SCRATCH/work
cd $GLOBAL_SCRATCH/work # move to the working directory

# setup the working environment
module load python/anaconda3
source activate py36 

# call the script and pass the region argument
python -u ~/projects/NHM_precipitation/hpc_scripts/aggregate_precip_to_HRU_HPC.py $reg

# move some files back to the home directory
cp ../hru_${reg}_stage_4_precip.cbh ~/projects/NHM_precipitation/data/
cp ../hru_${reg}_stage_4_precip.pcl ~/projects/NHM_precipitation/data/

cp ../hru_${reg}_stage_4_precip_prop.cbh ~/projects/NHM_precipitation/data/
cp ../hru_${reg}_stage_4_precip_prop.pcl ~/projects/NHM_precipitation/data/

# once finished, clean up
#rm ../HUC_${reg}_hruID_*.tiff
