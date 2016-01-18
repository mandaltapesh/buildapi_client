from setuptools import setup, find_packages

setup(
    name='buildapi_client',
    version='0.2.3.dev0',
    packages=find_packages(),

    install_requires=[
        'requests>=2.5.1'
    ],

    # Meta-data for upload to PyPI
    author='Armen Zambrano G.',
    author_email='armenzg@mozilla.com',
    description="Package designed to trigger jobs through Release Engineering's "
                "buildapi self-serve service.",
    license='MPL2',
    url='https://github.com/armenzg/buildapi_client',
)
