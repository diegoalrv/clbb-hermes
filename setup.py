from setuptools import setup, find_packages

version = "0.1.5.6"

setup(
    name='clbb-hermes',
    version=version,
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