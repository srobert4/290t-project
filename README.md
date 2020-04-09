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

# Getting Started

* Example code to load data into your graph, add annotations and analyze annotations is in `Example notebook.ipynb`

# Class Structure

* `Data_Loader`

The `Data_Loader` class exports functions to scrape data from Reddit and load it into your Neo4j graph using `py2neo`

    * `Scraper` - the scraper class interfaces with the Reddit API through `praw`
    * Object-Graph Mapping - `nodes.py` contains the Object-Graph Mapping. It defines a class for each node type in the Reddit graph

* `Data_Viewer`

The `Data_Viewer` class exports functions to query the graph and view the data. There are functions to view content and to view nodes.

* `Annotator`

The `Annotator` class exports functions to add annotations (`Code` nodes) to content (`Submission` and `Comment` nodes) in the graph.
