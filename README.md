# SAM SUBJOBSERVER

This server lets you queue your own jobs outside of the SAM qsub queue.The advantages are:

- No need to write custom code to run multiple jobs on the same reserved SAM node. (i.e. no need to say run the first 100 materials on node1, the second 100 materials on node2, etc).
- Can queue all the jobs you want to run without reserving any SAM resources.
- Can launch as many SAM resources as you want at any time to burn through the queue. If it isn't going fast enough, add more SAM resources later.

## Sample Code

See ./sample for example code to queue jobs on the server:

- sample_job.py is a sample job file, i.e. the difficult work you need run on a supercomputer.
- sample_enqueue.py is a sample enqueuing script, that enqueues the sample job to run later.

To test this locally, `cd sample` and run each of these in a different terminal window:

- `redis-server`
- `python sample_enqueue.py`
- `rq worker sample_queue`

