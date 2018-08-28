#!/bin/bash
# Script to move files and then run the aggregation script
# Theodore Barnhart | tbarnhart@usgs.gov

#SBATCH --job-name=convert_NLDASv2 # name that you chose
#SBATCH -n 1            # number of cores needed
#SBATCH -p normal                         # the partition you want to use, for this case prod is best
#SBATCH --account=wymtwsc        # your account
#SBATCH --time=48:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs.
#SBATCH --mail-type=ALL         # Send email on all events
#SBATCH --mail-user=tbarnhart@usgs.gov
#SBATCH  -o %j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)

source activate py36
cd ~/projects/NHM_precipitation/data/NLDASv2

for fl in `find -type f -name '*.grb'`; do

    gdal_translate -of Gtiff -b 1 -b 10 $fl ../NLDASv2_TP/${fl}.TP.tiff
    echo $fl

done