#!/bin/bash
# script to download the livneh2016 data set to yeti
# Theodore Barnhart | tbarnhart@usgs.gov 
#SBATCH --job-name=clip_hru # name that you chose 
#SBATCH -n 1            # number of cores needed 
#SBATCH -p normal                         # the partition you want to use, for this case prod is best 
#SBATCH --account=wymtwsc        # your account 
#SBATCH --time=15:00:00           # Overestimated guess at time, the process will be cancelled at the time limit (this case 6 hours), prod allows 21 day jobs. 
#SBATCH --mail-type=ALL         # Send email on all events 
#SBATCH --mail-user=tbarnhart@usgs.gov 
#SBATCH  -o clip_%j.log                    # Sets output log file to %j ( will be the jobId returned by sbatch)
#SBATCH --mem=6000            #memory in MB  

cd /home/tbarnhart/projects/NHM_precipitation/data/livneh2016/ # move to the correct directoy
wget -N ftp://livnehpublicstorage.colorado.edu/public/Livneh.2016.Dataset/Meteorology.netCDF/*.nc
