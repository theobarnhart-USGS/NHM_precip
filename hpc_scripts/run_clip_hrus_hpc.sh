reg=$1 # extract the region from the command

# move some things to the node
mkdir $GLOBAL_SCRATCH/AEA_tiffs
cd $GLOBAL_SCRATCH
cp ~/projects/NHM_precipitation/data/hrap_grid_AEA_idx_476_25.tiff ./

# setup the working environment 
module load python/anaconda3
source activate py36

python ~/projects/NHM_precipitation/clip_hrus_hpc.py $reg
cp ./AEA_tiffs/*.tiff ~/projects/NHM_precipitation/data/AEA_tiffs_regHRU/ # move the new clipped tiffs into my home directory
