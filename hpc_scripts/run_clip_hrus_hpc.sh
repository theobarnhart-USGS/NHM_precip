#!/bin/bash
# script to clip HRUs on Yeti
# Theodore Barnhart | tbarnhart@usgs.gov 
#SBATCH --job-name=clip_hru # name that you chose 
#SBATCH -n 1            # number of cores needed 
#SBATCH -p normal                         # the partition you want to use, for this case prod is best 
#SBATCH --account=wymtwsc        # your account 
#SBATCH --time=48:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs. 
#SBATCH --mail-type=ALL         # Send email on all events 
#SBATCH --mail-user=tbarnhart@usgs.gov 
#SBATCH  -o clip_%j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)
#SBATCH --mem=6000            #memory in MB  

reg=$1 # extract the region from the command
echo Starting: $reg

# setup the working environment 
source activate py36

python ~/projects/NHM_precipitation/clip_hrus_hpc.py $reg