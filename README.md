# 290t-project

# Set up

## Python environment
* Tested on Python 3.7

### For MacOS
* Create virtual environment: `python -m venv myenv`
* Activate virtual environment `source myenv/bin/activate`
* Install required packages: `pip install -r requirements.txt`
* Add virtual environment to jupyter: `python -m ipykernel install --user --name=myenv`
* [More detailed instructions for using jupyter notebooks with virtual environments](https://janakiev.com/blog/jupyter-virtual-envs/)

### For WindowsOS
* Create virtual enviroment: `python -m venv myenv`
* Activate virtual environment: `myenv/Scripts/activate`
* Install required packages: `pip install -r "<folder path>/requirements.txt"`
* Add virtual environment to Jupyter: `python -m ipykernel install --user --name=myenv`

## Neo4j
* Download neo4j desktop - add instructions for set up here

## Reddit API
* Create a Reddit account and set up an app following the [quick start instructions](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps)

## Credentials
* Copy neo4j and reddit credentials into config.txt and then move this file to /etc/ (or somewhere else, but then change data_loader.py and scraper.py to reflect this)
* Neo4j graph server needs to be running in order to use the data_loader module.
