# code_viewer.py
# Queries the graph for codes and displays results

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
import pandas as pd

class Code_Viewer:
    # The data viewer class allows the user to query the database and display results

    def __init__(self, graph):
        self.graph = graph
        self.rship_matcher = pn.RelationshipMatcher(self.graph)
        self.node_matcher = pn.NodeMatcher(self.graph)


    def get_code_table(self):
        # Returns a pandas dataframe containing all of the leaf codes with count
        return self.graph.run(
            "MATCH (c:Code)-[r:CODED]->(content) RETURN c.code, c.description, count(r)"
        ).to_data_frame().rename(
            columns = {"c.code" : "code", "c.description" : "description", "count(r)" : "count"}
        )

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

    def get_code_hierarchy(self):
        codes = Code.match(self.graph)
        labels = {
            'code' : [],
            'parent_codes' : []
        }
        for code in codes:
            if len(code.excerpts) > 0:
                labels['code'].append(code.code)
                labels['parent_codes'].append(str(code))

        return pd.DataFrame(data = labels)
