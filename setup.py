from setuptools import setup

setup(name="Hackathon",
      packages=["orangehackathon"],
      package_data={"orangehackathon": ["icons/*.svg"]},
      classifiers=["Example :: Invalid"],
      # Declare orangedemo package to contain widgets for the "Hackathon" category
      entry_points={
          # "orange.widgets": "Hackathon = orangehackathon",
          'orange3.addon': (
              'hackathon = orangehackathon',
          ),
          # Entry point used to specify packages containing tutorials accessible
          # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
          # 'orange.widgets.tutorials': (
          #     # Syntax: any_text = path.to.package.containing.tutorials
          #     'exampletutorials = orangecontrib.text.tutorials',
          # ),

          # Entry point used to specify packages containing widgets.
          'orange.widgets': (
              # Syntax: category name = path.to.package.containing.widgets
              # Widget category specification can be seen in
              #    orangecontrib/text/widgets/__init__.py
              'Hackathon = orangehackathon.widgets',
          ),

          # Register widget help
          # "orange.canvas.help": (
          #     'html-index = orangecontrib.text.widgets:WIDGET_HELP_PATH',),

      },
      )
