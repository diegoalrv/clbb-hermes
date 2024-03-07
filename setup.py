from setuptools import setup, find_packages

setup(
    name='clbb-hermes',
    version='0.1.2',
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