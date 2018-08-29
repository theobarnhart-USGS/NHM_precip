import subprocess

for reg in ['01','02','03','04','05','06','07','08','09','10U','10L','11','12','13','14','15','16','17','18']:
	cmd = 'sbatch run_clip_hrus_hpc.sh %s'%(reg)
	print('Submitting Region: %s'%reg)
	subprocess.call(cmd,shell=True)


