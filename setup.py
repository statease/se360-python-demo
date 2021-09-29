""" Demo code for SE360 """

from setuptools import setup

VERSION = '0.1.0'
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
        long_description="\n".join(DOCLINES[2:]),
        classifiers=CLASSIFIERS,
        author='Hank Anderson',
        author_email='hank@statease.com',
        license='Other/Proprietary License',
        url='https://statease.com/docs/se360/python-integration/',
        packages=['se360demo'],
        install_requires=['statease', 'requests', 'matplotlib', 'numpy', 'sklearn'],
        long_description_content_type='text/markdown',
    )

run_setup()
