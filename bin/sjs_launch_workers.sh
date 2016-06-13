#!/bin/bash

num_workers=$1
stay_alive=$2

rq_args="-b"
if [ "$stay_alive" == "1" ]; then
  rq_args=""
fi

# must explicitly set LC_ALL and LANG to run `rq worker` because of its dependency on 'Click'
export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8

mkdir -p logs

# This file must be run from the application directory
hostname=`uname -n`
timestamp=`date +"%Y_%m_%d__%H_%M_%S"`
pids=""
echo "launching $numworkers workers..."
for i in `seq 1 $num_workers`; do
  rq worker $rq_args -c settings.rq_worker_config > logs/${hostname}_${timestamp}_$i.log 2>&1 &
  pids="$pids $!"
done
echo "$num_workers launched. pids: $pids"

echo `date`
echo "waiting until all workers finish..."

wait $pids

echo "workers finished."
echo end_time: `date`
