from distutils.core import setup

setup(
    name="sam_subjobserver",
    version="0.1",
    py_modules=[],
    scripts=['bin/sjs_launch_workers.sh', 'bin/sjs_status.py'],
    )

# install_requires=[
#     'redis',
#     'rq'
# ],
