from setuptools import setup, find_packages

setup(
    name='buildapi_client',
    version='0.1',
    packages=find_packages(),
	
    install_requires=[
        'requests>=2.5.1'
    ],

    # Meta-data for upload to PyPI
    author='Armen Zambrano G.',
    author_email='armenzg@mozilla.com',
    description="Script designed to trigger jobs through Release Engineering's buildapi self-serve service.",
    license='MPL2',
    url='https://github.com/mozilla/build-buildapi',
)