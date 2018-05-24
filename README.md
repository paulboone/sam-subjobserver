# SJS

SJS has code for running a sub job server and code for managing your data provenance.


# SAM SUBJOBSERVER

This server lets you queue your own jobs outside of the CRC slurm queue. The advantages are:

- No need to write custom code to run multiple jobs on the same reserved CRC node. (i.e. no need to say run the first 100 materials on node1, the second 100 materials on node2, etc).
- Can queue all the jobs you want to run without reserving any CRC resources.
- Can launch as many CRC resources as you want at any time to burn through the queue. If it isn't going fast enough, add more CRC resources later.


## Recommended environment setup for CRC

The recommended environment is python 3.5, and a venv for your the project's requirements.

First time project setup:

```
module purge
module load python/intel-3.5

# Create virtual environment
mkdir -p ~/venv
pyvenv --without-pip ~/venv/{your_project_name}
source ~/venv/{your_project_name}/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source ~/venv/{your_project_name}/bin/activate

cd {path to your project}

pip install -r requirements.txt
```

When you want to run your project in the future:

```
module purge
module load python/intel-3.5
source ~/venv/{your_project_name}/bin/activate
cd {path to your project}
```

Those commands will also be in your slurm script.

## Configuration setup

The jobserver expects there to be a settings directory at the root level of your project. This directory should be a python module (i.e. include a __init__.py file). It should contain an sjs.yaml file.

You can copy the sample_settings directory from this project to your project as a starting point. Whoever deploys your software should configure the config file specifically to the deployment environment. When you run your project locally to test, you should copy the config file (removing the '.sample') and adjust for your local environment. The sample files are setup right now to work with minimal changes on a local install.

Each project should run from its own database, so make sure you ask for a unique database_id to place in your config files.

## Running on CRC

Running your job on CRC will take two steps: 1) queuing the work on the subjobserver and then 2) running a slurm file to load workers on the H2P cluster.

### Queueing the work

To queue your work on the subjobserver, start with a script that runs all your work serially. You should have a method that runs a unit of work, which could be one material simulation, one paired interpenetration test, one RASPA run, a set of RASPA runs across a material type, etc. That method should have parameters that fully define what it needs to do, i.e. you should be able to load up a python console, import the file your method is in, then call your method with the parameters you want, and have it do the work you want it to do. As long as that is the case, queuing that unit of work, rather than running it, is trivial and looks like this:

```
from sample_job import job_that_takes_a_long_time
import sjs
sjs.load(os.path.join("settings","sjs.yaml"))
job_queue = sjs.get_job_queue()

## run the job normally...
job_that_takes_a_long_time(10)

## or queue the job on the subjobserver...
job_queue.enqueue(job_that_takes_a_long_time, 10)
```

Once your job is queued, it won't run until you launch some resources on the HPC cluster. Until then it will sit in the queue. You can use the command `sjsmon` or `rq info -u redis://{your_redis_url}` to look at the contents of the queue.

### Launching workers on the HPC cluster

You will need a qsub script in your project. See sample/launch_workers_qsub.sh for a template you can start with. The qsub file does a few main things:

- it loads python and the venv
- it runs sjs_launch_workers.sh with parameters for number of workers to run and whether the workers should stay alive after the queue is empty.
- cleanup

You should be able to use the qsub sample file as-is except for changing the PBS parameters and loading the venv specific to your project.

You must run the qsub script from your project root.

## Additional sample code for standalone interaction with the subjobserver

See ./sample/standalone-example for example code to queue jobs on the server:

- sample_job.py is a sample job file, i.e. the difficult work you need run on a supercomputer.
- sample_enqueue.py is a sample enqueuing script, that enqueues the sample job to run later.

To test this locally, `cd sample/standalone-example` and run each of these in a different terminal window:

- `redis-server`
- `python sample_enqueue.py`
- `rq worker sample_queue`


## Cheat sheet

Two views of checking what is happening on the job server:

one-time:
```
rq info -u redis://10.201.0.11:6379/1
sjs_status.py settings/sjs.yaml
```

ongoing:

```
watch rq info -u redis://10.201.0.11:6379/{your db #}
watch sjs_status.py settings/sjs.yaml
```

Variations of launching workers on the cluster:

```
# launch with default settings
qsub launch_workers_qsub.sh

# launch but keep workers running, even if the queue is empty
# (useful when running multi-generational jobs)
qsub -v stay_alive=1 launch_workers_qsub.sh

# launch four cores on one node
qsub -l nodes=1:ppn=4 launch_workers_qsub.sh


# launch four cores each on two nodes
qsub -l nodes=1:ppn=4 launch_workers_qsub.sh
qsub -l nodes=1:ppn=4 launch_workers_qsub.sh

### NOTE THAT I RAN THE COMMAND TWICE, AND DID NOT RUN:
# qsub -l nodes=2:ppn=4 launch_workers_qsub.sh
# frank does not easily support multi-node jobs. This will be improved with the new cluster
# upgrade happening later this year!
```

Debugging problems:

```
## requeue all failed jobs
rq requeue -a -u redis://10.201.0.11:6379/{your db #}

## delete all queued jobs
rq empty -a -u redis://10.201.0.11:6379/{your db #}

```

See `rq --help` for more information and more detail on those commands.
