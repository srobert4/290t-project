# code_viewer.py
# Queries the graph for codes and displays results

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
from termcolor import colored

class Code_Viewer:
    # The data viewer class allows the user to query the database and display results

    def __init__(self, graph):
        self.graph = graph
        self.rship_matcher = pn.RelationshipMatcher(self.graph)
        self.node_matcher = pn.NodeMatcher(self.graph)


    def view_coded(self, code_label):
        raise NotImplementedError
        # View all content coded with a given code. The code label should be the label
        # of the leaf node
        # code = Code.match(self.graph, code_label).first()
        # if not code:
        #     print("Code not found")
        #     return
        #
        # content = []
        # for content_node in code.excerpts:
        #     highlight = code.excerpts.get(content_node, "text")
        #     content += [colored(highlight, "yellow").join(str(content_node).split(highlight))]
        #
        # return self._construct_result_string(
        #     f"Content with code: {code_label}",
        #     content
        # )
