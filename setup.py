""" Demo code for SE360 """

from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '0.1.2'
DOCLINES = (__doc__ or '').split("\n")

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "License :: Other/Proprietary License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Information Analysis",
]

def run_setup():
    setup(
        name='se360demo',
        version=VERSION,
        description=DOCLINES[0],
        long_description=long_description,
        classifiers=CLASSIFIERS,
        author='Hank Anderson',
        author_email='hank@statease.com',
        license='Other/Proprietary License',
        url='https://github.com/statease/se360-python-demo',
        packages=['se360demo'],
        package_data={'se360demo': [ 'data/*.dxpx', 'data/*.csv', 'examples/*.py' ] },
        install_requires=['statease', 'requests', 'matplotlib', 'numpy', 'sklearn'],
        long_description_content_type='text/markdown',
    )

run_setup()
