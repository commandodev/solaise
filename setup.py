from setuptools import setup, find_packages
import py2exe

version = '0.0'

setup(name='solaise_cards',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ben Ford',
      author_email='ben.fordnz@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      console=['solaise_cards/console_cards.py'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
