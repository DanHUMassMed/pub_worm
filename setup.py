"""
Setup for pypi releases of pub_worm
"""
from pub_worm import __version__
from setuptools import setup, find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='pub_worm',
      version=__version__,
      description='Wormbase/PudMed API Access',
      long_description_content_type="text/markdown",
      long_description=long_description,

      url='https://github.com/DanHUMassMed/pub_worm.git',
      author='Dan Higgins',
      author_email='daniel.higgins@yahoo.com',
      license='MIT',

      packages=find_packages(),
      install_requires=[
            'pandas==2.2.3',
            'beautifulsoup4==4.12.3',
            'requests==2.31.0',
            'aiohttp==3.9.5',
            'aiofiles==24.1.0'
      ],
      include_package_data=True,
      zip_safe=False)
