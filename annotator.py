# annotator.py
# Adds codes to content

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
from scraper import Reddit
import configparser
import time

class Annotator:
    # The data loader class is responsible for using a scraper to get data from
    # Reddit and adding it to the Neo4j database
    cfg = configparser.ConfigParser()
    # ==============================
    # If you move your config file:
    # change the following line to its chosen location
    # ==============================
    cfg.read('/etc/290t-config.txt')
    cfg = cfg['neo4j']

    def __init__(self):
        self.graph = pn.Graph(auth=(self.cfg['db'], self.cfg['pw']))

    def parse_code(self, code):
        # input: code1: subcode1; code2: subcode2
        # output: list of lists. for each list: ordered from highest level to lowest level code
        codes = code.split(";")
        return [c.strip().split(":") for c in codes]


    def annotate(self, code, content_node, content):
        # take a code1: subcode1: subcode2; code2: subcode3 and return code nodes
        codes = self.parse_code(code)
        for code_levels in codes:
            self.add_codes(code_levels, content_node, content)

    def get_code(self, code_label):
        return Code.match(self.graph, code_label).first()

    def add_codes(self, code_levels, content_node, content):
        self.add_code(code_levels.pop(0), code_levels, content_node, content)

    def add_code(self, code_label, children, content_node, content):
        code = self.get_code(code_label)
        if not code:
            code = Code(code_label)

        if len(children) == 0:
            self.add_content(code, content_node, content)
        else:
            child = self.add_code(children.pop(0), children, content_node, content)
            code.subcodes.add(child)

        self.graph.push(code)
        return code

    def add_content(self, code, content_node, content):
        if content_node.__primarylabel__ == "Submission":
            code.submission_excerpts.add(content_node, text = content)
        else:
            code.comment_excerpts.add(content_node, text = content)
