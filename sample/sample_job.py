#
# This job file should contain ALL THE WORK of your job. The method here is what you'll be enqueuing
# in the enqueue script.
#



from random import random
from time import sleep

def job_that_takes_a_long_time(long_time = 30):
  random_var = int(random()*10000)
  
  print("starting job with random_var = %s" % random_var)
  print("sleeping for %s" % long_time)
  
  sleep(long_time)
  
  print("ending job with random_var = %s" % random_var)
  return random_var