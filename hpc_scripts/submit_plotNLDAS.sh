#!/bin/bash
# Script to move files and then convert pcl to cbh for the NHM
# Theodore Barnhart | tbarnhart@usgs.gov
# 20180417
#SBATCH --job-name=convNLDAS # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=04:00:00           # Overestimated guess at time
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=20000            #memory in MB

reg=$1 # parse the first argument passed to the wrapper

source activate py36

python -u plotNLDASforcings.py $reg
