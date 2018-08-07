import os
from setuptools import setup, find_packages

version = '0.1.1.dev1'

proj_dir = os.path.abspath(os.path.dirname(__file__))
reqs = [line.strip()
        for line in open(
                os.path.join(proj_dir, 'requirements.txt'), encoding='utf-8')]

setup(
    name='radcalnet',
    version=version,
    author='Slava Kerner, Amit Aronovitch',
    url='https://github.com/satellogic/radcalnet',
    author_email='amit@satellogic.com',
    description="""\
Python package for easy access to the measurements published by RadCalNet.org
""",
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    install_requires=reqs
)
