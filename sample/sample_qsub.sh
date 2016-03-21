#!/bin/bash
#
# Example shell script for running job that runs off the Wilmerlab subjobserver.
# $Revision: 1.0 $
# $Date:  2016-03-21 $
# $Author: paulboone $

#PBS -j oe
#PBS -N index_refs
#PBS -q test
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:00:15
#PBS -l mem=1GB
#PBS -S /bin/bash

echo JOB_ID: $PBS_JOBID JOB_NAME: $PBS_JOBNAME HOSTNAME: $PBS_O_HOST
echo start_time: `date`

# dependencies
module load python/anaconda3-2.3.0-rhel


# must explicitly set LC_ALL and LANG to run `rq worker` because of its dependency on 'Click'
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8

# This file must be run from the ./sample directory
rq worker sample_queue

echo end_time: `date`

# workaround for .out / .err files not always being copied back to $PBS_O_WORKDIR
cp /var/spool/torque/spool/$PBS_JOBID.OU $PBS_O_WORKDIR/$PBS_JOBID.out
cp /var/spool/torque/spool/$PBS_JOBID.ER $PBS_O_WORKDIR/$PBS_JOBID.err 

exit