#!/bin/bash
#SBATCH --job-name=zip_NLDAS # name that you chose
#SBATCH -n 8            # number of cores needed
#SBATCH --ntasks-per-node 8
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=18:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)  
#SBATCH --mem=25000            #memory in MB 

cd ../data/NLDASv2_daily_cbh/

for fl in *.cbh ; do
	basefl=$(basename $fl)

	/usr/bin/7za a -tzip -mmt -mx9 /cxfs/projects/usgs/water/wymtwsc/tbarnhart/projects/NHM_precipitation/transfer/NLDASv2/${basefl}.zip
done
