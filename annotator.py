# annotator.py
# Adds codes to content

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
import configparser

class Annotator:
    # The annotator class is responsible for adding annotations to content
    cfg = configparser.ConfigParser()
    # ==============================
    # If you move your config file:
    # change the following line to its chosen location
    # ==============================
    cfg.read('/etc/290t-config.txt')
    cfg = cfg['neo4j']

    def __init__(self):
        self.graph = pn.Graph(auth=(self.cfg['db'], self.cfg['pw']))

    def annotate(self, code, content_id, content_type, content):
        # code: an annotation in the format code1: subcode; code2: subcode
        # content_id: the Reddit id of the content node
        # content_type: Comment or Submission
        # content: the substring of the content to be annotated
        if content_type == "Submission":
            content_node = Submission.match(self.graph, content_id).first()
        else:
            content_node = Comment.match(self.graph, content_id).first()

        codes = self.parse_code(code)
        for code_levels in codes:
            self.add_codes(code_levels, content_node, content)

    def parse_code(self, code):
        # input: code1: subcode1; code2: subcode2
        # output: list of lists. for each list: ordered from highest level to lowest level code
        codes = code.split(";")
        return [c.strip().split(":") for c in codes]

    def get_code(self, code_label):
        return Code.match(self.graph, code_label).first()

    def add_codes(self, code_levels, content_node, content):
        code = self.add_code(code_levels.pop(0), code_levels, content_node, content)
        self.graph.push(code)

    def add_code(self, code_label, children, content_node, content):
        code = self.get_code(code_label)
        if not code:
            code = Code(code_label)

        if len(children) == 0:
            self.add_content(code, content_node, content)
        else:
            child = self.add_code(children.pop(0), children, content_node, content)
            child.parent_code.add(code)
            self.graph.push(child)

        return code

    def add_content(self, code, content_node, content):
        if content_node.__primarylabel__ == "Submission":
            code.submission_excerpts.add(content_node, text = content)
        else:
            code.comment_excerpts.add(content_node, text = content)
