from setuptools import setup,find_packages

setup(
    name='otavite',
    version='0.1',
    description='A simple cadmium library for generating jobs and solving the into gcode',
    packages=['otavite'],
    install_requires=[
        'cadmium',
        'numpy',
        'networkx',
        'pygcode',
        'more_itertools',
        'toolz'
    ],
    license='GNU'
)