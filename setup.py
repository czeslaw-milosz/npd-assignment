from setuptools import setup

setup(
    name="npd_assignment",
    version="0.1.0",
    author="Radosław Jurczak",
    author_email="radoslaw.jurczak@student.uw.edu.pl",
    packages=["npd_assignment", "npd_assignment.test"],
    license="LICENSE.txt",
    description="Final assignment for Data Analysis in Python course @ MIM UW",
    install_requires=[
        "argparse",
        "pandas>=1.5",
        "pytest",
        "tabulate",
    ],
)
