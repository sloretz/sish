from setuptools import find_packages
from setuptools import setup
from sish import __version__

with open("README.rst", "r") as fin:
    long_description = fin.read()

setup(
    name='sish',
    version=__version__,
    packages=find_packages(),
    package_data={'sish': ['templates/*.in']},
    author='Shane Loretz',
    author_email='shane.loretz@gmail.com',
    description='CLI tools for writing code in apptainer containers.',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/sloretz/sish",
    license='Apache-2.0',
    install_requires=[
        'argcomplete',
        'packaging',
        'importlib_resources; python_version < "3.7"'
    ],
    entry_points={
        'console_scripts': [
            'create-sish-container = sish.cli:main_create_sish_container',
            'sish = sish.cli:main_sish',
            'rsish = sish.cli:main_rsish',
        ]
    }
)
