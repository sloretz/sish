from setuptools import setup
from siws import __version__

with open("README.rst", "r") as fin:
    long_description = fin.read()

setup(
    name='siws',
    version=__version__,
    packages=['siws'],
    package_data={'siws': ['templates/*.tmpl']},
    author='Shane Loretz',
    author_email='shane.loretz@gmail.com',
    description='CLI tools for writing code in singularity containers.',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/sloretz/siws",
    license='Apache-2.0',
    install_requires=[
        'argcomplete',
        'packaging',
        'importlib_resources; python_version < "3.7"'
    ],
    entry_points={
        'console_scripts': [
            'create-sish-container = siws.cli:main_create_sish_container',
            'sish = siws.cli:main_sish',
            'rsish = siws.cli:main_rsish',
        ]
    }
)
