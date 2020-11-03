import os

from setuptools import setup, find_packages

INSTALL_REQUIRES = sorted(set(
    line.partition('#')[0].strip()
    for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt'))
) - {''})

setup(name="orangehackathon",
      packages=find_packages(),
      package_data={"orangehackathon": ["icons/*.svg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "UTwente" category
      entry_points={"orange.widgets": "UTwente = orangehackathon.widgets"},
      install_requires=INSTALL_REQUIRES,
      )
