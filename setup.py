"""
Setup for pypi releases of pub_worm
"""
from setuptools import setup, find_packages
from pathlib import Path

# rm -rf dist
# python setup.py sdist
# pip install dist/wormcat_batch-1.0.1.tar.gz
# twine check dist/*
# twine upload --repository pypi dist/*


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='pub_worm',
      version='0.2.2',
      description='Wormbase/PudMed API Access',
      long_description_content_type="text/markdown",
      long_description=long_description,

      url='https://github.com/DanHUMassMed/pub_worm.git',
      author='Dan Higgins',
      author_email='daniel.higgins@yahoo.com',
      license='MIT',

      packages=find_packages(),
      install_requires=['pandas'],
      include_package_data=True,
      zip_safe=False)
