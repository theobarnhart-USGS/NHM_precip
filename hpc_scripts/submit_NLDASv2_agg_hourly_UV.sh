#!/bin/bash
#SBATCH --job-name=aggNLDAS # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p UV                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=72:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=150000            #memory in MB 

echo Starting: $1

# Script to move files and then run the aggregation script
# Theodore Barnhart | tbarnhart@usgs.gov
# 20181001

reg=$1 # parse the first argument passed to the wrapper

# setup the working environment
source activate py36 

# call the script and pass the region argument
srun python -u  ~/projects/NHM_precipitation/hpc_scripts/aggregate_NLDASv2_daily.py $reg
