# 290t-project

# Set up

* Create venv, `pip install -r requirements.txt`
* Download neo4j desktop - add instructions for set up here
* Create a Reddit account and set up an app ([quick start instructions](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps))
* Copy neo4j and reddit credentials into config.txt and then move this file to /etc/ (or somewhere else, but then change data_loader.py and scraper.py to reflect this)
* Neo4j graph server needs to be running in order to use the data_loader module.
