#for year in {1979..2017}; do
for year in {1984,1986,1993,1995,1996,1997,2002,2003,2005,2007,2010,2011,2012,2013}; do
	sbatch get_missing_NLDASv2.sh $year
	sleep 10
done
