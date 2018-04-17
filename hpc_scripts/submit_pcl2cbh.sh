#!/bin/bash
# Script to move files and then convert pcl to cbh for the NHM
# Theodore Barnhart | tbarnhart@usgs.gov
# 20180417
#SBATCH --job-name=convert_liv # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=5:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=20000            #memory in MB

reg=$1 # parse the first argument passed to the wrapper
echo 'Starting Region '${reg}'.'

# move files to the node:
cp ~/projects/NHM_precipitation/data/livneh_*_reg_${reg}.pcl $GLOBAL_SCRATCH/ # move the forcing data to local drive

cd $GLOBAL_SCRATCH

# setup the working environment
module load python/anaconda3
source activate py36 

# call the script and pass the region argument
for var in {'Prec','Tmin','Tmax'}; do
	
	infl=./livneh_${var}_reg_${reg}.pcl
	outfl=./livneh2016_region_${reg}_${var}.cbh
	python -u ~/projects/NHM_precipitation/hpc_scripts/pickle2cbh.py $reg $var $infl $outfl
done
# move finished files to storage
echo 'Copying cbh files to storage.'
cp livneh2016_region_${reg}_*.cbh /cxfs/projects/usgs/water/wymtwsc/tbarnhart/projects/NHM_precipitation/transfer/livneh2016/
echo 'Region '${reg}' complete.'
