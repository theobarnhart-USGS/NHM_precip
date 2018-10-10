#!/bin/bash
#SBATCH --job-name=h2d # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=80:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=10000            #memory in MB 

# Theodore Barnhart | tbarnhart@usgs.gov
# 20181001

# setup the working environment
source activate py36 

# call the script and pass the region argument
srun python -u  ~/projects/NHM_precipitation/hpc_scripts/NLDAS_hour2day.py
