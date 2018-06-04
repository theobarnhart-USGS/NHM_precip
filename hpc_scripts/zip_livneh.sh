#!/bin/bash
#SBATCH --job-name=zip_livneh # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=10:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=25000            #memory in MB 

cd /cxfs/projects/usgs/water/wymtwsc/tbarnhart/projects/NHM_precipitation/transfer/livneh2016/
find . -name '*10U*.cbh' -print -exec zip -9 '{}'.zip '{}' \;
