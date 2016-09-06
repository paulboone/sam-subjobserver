from setuptools import setup
import versioneer

setup(
    name="wilmerlab-sjs",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'click',
        'pyyaml',
        'redis',
        'rq',
    ],
    include_package_data=True,
    packages=['sjs'],
    entry_points={
        'console_scripts': [
            'sjs=sjs.scripts.run_start:run_start',
            'sjs_monitor=sjs.scripts.supervisor:monitor',
            'sjs_launch_workers=sjs.scripts.launch_workers:launch_workers',
            'sjs_env_record=sjs.scripts.env_record:env_record',
            'sjs_run_end=sjs.scripts.run_end:run_end',
        ]
    },
)
