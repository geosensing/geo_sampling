from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        print("TODO: PostDevelopCommand")
        super().run()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        print("TODO: PostInstallCommand")
        super().run()

class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    
    def initialize_options(self):
        super().initialize_options()
        self.tox_args = None

    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        import shlex
        args = shlex.split(self.tox_args) if self.tox_args else None
        tox.cmdline(args=args)

setup(
    name='geo-sampling',
    version='0.1.0',  # Increment version for Python 3.10+
    description='Scripts for sampling Geo data sets by the specific region name',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url='https://github.com/soodoku/geo_sampling',
    author='Suriyan Laohaprapanon, Gaurav Sood',
    author_email='suriyant@gmail.com, gsood07@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='geo street road openstreetmap osm city',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'script']),
    python_requires=">=3.10",
    install_requires=[
        'pyshp>=2.3.1',
        'matplotlib>=3.5.0',
        'pyproj>=3.3.0',
        'Shapely>=2.0.0',
        'utm>=0.7.0',
        'beautifulsoup4>=4.10.0',
        'requests>=2.32.0'
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    package_data={'geo_sampling': []},
    entry_points={
        'console_scripts': [
            'geo_roads=geo_sampling.geo_roads:main',
            'sample_roads=geo_sampling.sample_roads:main',
        ],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
        'test': Tox,
    },
    tests_require=['tox'],
)