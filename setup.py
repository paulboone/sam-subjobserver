from setuptools import setup, find_packages
import versioneer

setup(
    name="sjs",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'click',
        'pyyaml',
        'redis',
        'rq',
    ],
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sjs=sjs.scripts.cli:cli',
            'sjsmon=sjs.scripts.monitor:monitor',
            'sjs_launch_workers=sjs.scripts.launch_workers:launch_workers',
        ]
    },
)
