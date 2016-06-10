from distutils.core import setup

setup(
    name="sjs",
    version="0.2",
    scripts=['bin/sjs_launch_workers.sh', 'bin/sjs_status.py'],
    install_requires=['redis'],
    packages=['sjs']
)
