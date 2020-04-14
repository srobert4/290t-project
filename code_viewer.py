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


    def get_code_table(self):
        # Returns a pandas dataframe containing all of the codes with count
        raise NotImplementedError
        # get all leaf code nodes
        # for each node count the number of children
        # convert to string
        # columns: full_code, top_level, bottom_level, description, count

    def get_top_words(self, code_label, n = 10):
        # Returns dataframe of most common words coded with the given code
        # code_label: code to find top words of
        # n: number of top words to return
        # Returns: DataFrame(word, count)
        raise NotImplementedError

    def get_similar_codes(self, code_label, n = 1):
        # Returns list of most similar codes to the given code label, ordered by similarity
        # code_label: code to find similar codes to
        # n: number of similar codes to return
        # Returns: ordered list of code labels
        raise NotImplementedError
