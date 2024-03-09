# pub_worm
API integration of Wormbase and NCBI Utils

Call from the commandline
$PYTHONPATH="./src" python -m pub_worm.wormbase.WormbaseREST

#### Deploy
* Advance the version number in setup.py
* `conda deactivate # twine is installed in base env`
* `increment setup.py version`
* `cd <project directory>`
* `rm -rf ./dist`
* `rm -rf ./wormcat_batch.egg-info`
* `python setup.py sdist`
* `twine check dist/*`
* `twine upload --repository pypi dist/*`
* `git add .`
* `git commit -m "some comment"`
* `git push`

