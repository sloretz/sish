from setuptools import setup
from singws import __version__

with open("README.rst", "r") as fin:
    long_description = fin.read()

setup(
    name='singws',
    version=__version__,
    packages=['singws'],
    package_data={'singws': ['templates/*.tmpl']},
    author='Shane Loretz',
    author_email='shane.loretz@gmail.com',
    description='CLI tools for writing code in singularity containers.',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/sloretz/singws",
    license='Apache-2.0',
    install_requires=[
        'argcomplete',
        'packaging'
    ],
    entry_points={
        'console_scripts': [
            'singws = singws.cli:main',
        ]
    }
)
