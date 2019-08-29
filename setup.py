from setuptools import setup, find_packages

setup(name="Hackathon",
      packages=[find_packages()],
      package_data={"orangehackathon": ["icons/*.svg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Hackathon" category
      entry_points={"orange.widgets": "Hackathon = orangehackathon"},
      )
