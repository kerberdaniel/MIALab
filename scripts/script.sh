#!/bin/bash


## META
#SBATCH --mail-user=matteo.tagliabue@students.unibe.ch
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --job-name="MIALAB test"

## Resources
#SBATCH --partition=epyc2 ## default cpu clusters
#SBATCH --qos=job_epyc2 ## default (running time limit 4 days), if requires longer running time use --qos=job_epyc2_long (15 days)
#SBATCH --cpus-per-task=1  ## CPU allocation
#SBATCH --mem-per-cpu=1G ## RAM allocation
#SBATCH --time=24:00:00 ## job running time limit (user setting)

## Environment
module load Anaconda3 ## load available module, show modules -> module avail
eval "$(conda shell.bash hook)" ## init anaconda in shell
conda activate mialab ## activate environment


## Run
sbatch --mail-user=matteo.tagliabue@students.unibe.ch --mail-type=BEGIN,FAIL,END --job-name="MIALAB test" --mem-per-cpu=32G --cpus-per-task=1 --wrap="python3 ../bin/main.py"
