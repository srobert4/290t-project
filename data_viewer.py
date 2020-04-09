# data_viewer.py
# Queries the graph and displays results

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
import configparser

class Data_Viewer:
    # The data viewer class allows the user to query the database and display results
    cfg = configparser.ConfigParser()
    # ==============================
    # If you move your config file:
    # change the following line to its chosen location
    # ==============================
    cfg.read('/etc/290t-config.txt')
    cfg = cfg['neo4j']

    def __init__(self):
        self.graph = pn.Graph(auth=(self.cfg['db'], self.cfg['pw']))

    def view_submission(self, submission_id, include_comments = False):
        # Query graph for a submission and display with all comments / replies
        submission = Submission.match(self.graph, submission_id).first()
        return str(submission)

    def view_user(self, user_name):
        # Query graph for all content created by a user
        raise NotImplementedError

    def view_subreddit(self, subreddit_id):
        # View all content on a subreddit
        raise NotImplementedError

    def view_coded(self, code_label):
        # View all content coded with a given code
        raise NotImplementedError

    def view_search(self, query):
        # View content that matches a search term
        raise NotImplementedError
