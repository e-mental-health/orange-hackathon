from setuptools import setup

setup(name="Hackathon",
      packages=["orangehackathon"],
      package_data={"orangehackathon": ["icons/*.svg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Hackathon" category
      entry_points={"orange.widgets": "Hackathon = orangehackathon"},
      )
