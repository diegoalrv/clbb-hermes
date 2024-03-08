from setuptools import setup, find_packages
from hermes.__init__ import __version__

setup(
    name='clbb-hermes',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'scipy',
        'numpy',
        'geopandas',
        'osmnx',
        'networkx',
        'pandana',
        'osmnet',
        'pyarrow',
        'openpyxl'
    ],
)