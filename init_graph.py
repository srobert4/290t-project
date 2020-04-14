# data_viewer.py
# Queries the graph and displays results

import py2neo as pn
import configparser
import logging

class Graph:
    # The data viewer class allows the user to query the database and display results
    cfg = configparser.ConfigParser()
    # ==============================
    # If you move your config file:
    # change the following line to its chosen location
    # ==============================
    cfg.read('/etc/290t-config.txt')
    cfg = cfg['neo4j']

    def __init__(self):
        try:
            self.graph = pn.Graph(auth=(self.cfg['db'], self.cfg['pw']))
        except:
            logging.warning("Problem loading graph: an Exception occurred")
            self.graph = None
        else:
            if self.graph:
                logging.info("Successfully connected to graph")
                print("Successfully connected to graph")
            else:
                logging.warning("Problem loading graph: py2neo.Graph() returned None")
