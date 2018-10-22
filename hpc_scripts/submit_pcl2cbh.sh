#!/bin/bash
# Script to move files and then convert pcl to cbh for the NHM
# Theodore Barnhart | tbarnhart@usgs.gov
# 20180417
#SBATCH --job-name=convNLDAS # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=15:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=20000            #memory in MB

reg=$1 # parse the first argument passed to the wrapper
echo 'Starting Region '${reg}'.'

# setup the working environment
source activate py36 

# call the script and pass the region argument
for var in {'P','Tmin','Tmax'}; do
	
	infl=~/projects/NHM_precipitation/data/NLDASv2_${var}_daily_reg_${reg}.pcl
	outfl=/home/tbarnhart/projects/NHM_precipitation/data/NLDASv2_daily_cbh/NLDASv2_daily_region_${reg}_${var}.cbh
	python -u pickle2cbh.py $reg $var $infl $outfl
done
echo 'Region '${reg}' complete.'