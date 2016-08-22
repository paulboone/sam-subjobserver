from setuptools import setup

setup(
    name="wilmerlab-sjs",
    version="0.2.1",
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
            'sjs_status=sjs.scripts.sjs_status:sjs_status',
        ]
    }
)
