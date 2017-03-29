from setuptools import setup, find_packages

version = '1.3'

setup(name='bhr-client',
    version=version,
    description="BHR Client",
    long_description="",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='bhr',
    author='Justin Azoff',
    author_email='JAzoff@illinois.edu',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "requests>=2.0",
        "arrow==0.10.0",
    ],
    extras_require = {
        'cli' : ['Click'],
    },
    entry_points = {
        'console_scripts': [
            'bhr-client = bhr_client.cli:main',
            'bhr-client-run-stdout = bhr_client.run:main',
        ]
    }
)
