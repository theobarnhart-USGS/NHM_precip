# Script to move files and then run the aggregation script
# Theodore Barnhart | tbarnhart@usgs.gov
# 20171106

reg=$1 # parse the first argument passed to the wrapper

# setup the working environment
module load python/anaconda3
source activate py36 

# call the script and pass the region argument
python ~/projects/NHM_precipitation/hpc_scripts/aggregate_livneh2016.py $reg
