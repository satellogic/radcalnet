import os
from setuptools import setup, find_packages

proj_dir = os.path.abspath(os.path.dirname(__file__))
reqs = [line.strip()
        for line in open(
                os.path.join(proj_dir, 'requirements.txt'), encoding='utf-8')]

setup(
    name='radcalnet',
    version='0.1.0.dev0',
    maintainer_email='amit@satellogic.com',
    packages=find_packages(),
    install_requires=reqs
)
