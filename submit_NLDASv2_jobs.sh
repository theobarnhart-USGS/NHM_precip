for year in {1979..2017}; do
	sbatch get_NLDASv2.sh $year
	sleep 5
done
