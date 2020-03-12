# data_loader.py
# Loads data to graph

import py2neo as pn
from scraper import Reddit
import configparser

class Data_Loader:
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
        self.subgraph = None
        self.scraper = Reddit()

        # TODO: These probably should only be executed in the case that we're creating
        # a new graph, which isn't necessarily the case.
        self.graph.schema.create_uniqueness_constraint("User", "id")
        self.graph.schema.create_uniqueness_constraint("Submission", "id")
        self.graph.schema.create_uniqueness_constraint("Comment", "id")
        self.graph.schema.create_uniqueness_constraint("Subreddit", "id")

    def clear_graph(self):
        # delete all nodes in the graph
        self.graph.delete_all()

    def commit_subgraph(self):
        # Commit the nodes currently in the subgraph to the remote graph
        if self.subgraph is None:
            return
        txn = self.graph.begin()
        txn.create(self.subgraph)
        txn.commit()
        self.subgraph = None

    def add(self, node_or_relationship):
        # add node or relationship to subgraph
        if self.subgraph is None:
            self.subgraph = node_or_relationship
        else:
            self.subgraph = self.subgraph | node_or_relationship

    def get_node(self, node_type, **kwargs):
        # check the remote graph for a node that has the given node_type and
        # properties matching kwargs. If it exists, return the node, else
        # return None
        nodes = self.graph.nodes.match(node_type, **kwargs)
        if len(nodes) > 0:
            return nodes.first()
        return None

    def load_submissions(self, submission_urls):
        # Given a list of Reddit submission urls, add all of the submissions
        # to the graph, including authors, subreddits and comments
        for submission in submission_urls:
            sub = self.scraper.get_submission(submission)
            if sub is not None:
                self.add_submission(sub)

    def add_submission(self, submission):
        # submission: praw Submission object to add to remote graph
        # If submission is not already in the remote graph, add it along
        # with the author and subreddit if not already in the graph, as well
        # as all its comments
        # If the submission already exists in the graph, do nothing.

        # If submission exists, return node
        sb = self.get_node("Submission", id=submission.id)
        if sb is not None:
            return sb

        # Add the subreddit if not already added to subgraph
        subreddit = self.add_subreddit(
            self.scraper.get_subreddit(source_content = submission)
        )

        # Add the author if not already added to subgraph
        author = self.add_author(
            self.scraper.get_author(source_content = submission)
        )

        # Add the submission to subgraph
        sb = pn.Node("Submission", **self.scraper.get_attributes(submission, "Submission"))
        self.add(sb)

        # Connect submission to author and subreddit
        if author is not None:
            posted = pn.Relationship(author, "POSTED", sb)
            self.add(posted)

        posted_on = pn.Relationship(sb, "POSTED_ON", subreddit)
        self.add(posted_on)

        self.commit_subgraph()

        # Add the comments to the subgraph
        for comment in self.scraper.get_comments(submission):
            c = self.add_comment(comment)

        return sb

    def add_subreddit(self, sr):
        # sr: praw Subreddit object
        # If subreddit exists in remote graph: return corresponding Node
        # Else: add subreddit to local subgraph and return new Node
        if sr is None: return None
        subreddit = self.get_node("Subreddit", id=sr.id)
        if subreddit is not None:
            return subreddit
        subreddit = pn.Node("Subreddit", **self.scraper.get_attributes(sr, "Subreddit"))
        self.add(subreddit)
        return subreddit

    def add_author(self, author):
        # author: praw Redditor object
        # If user exists in remote graph: return corresponding Node
        # Else: add user to local subgraph and return new Node
        if author is None: return None
        user = self.get_node("User", name = author.name)
        if user: return user
        user = pn.Node("User", **self.scraper.get_attributes(author, "author"))
        self.add(user)
        return user

    def add_comment(self, comment):
        # comment: praw comment object to add to remote graph
        # If comment is not already in the remote graph, add it along
        # with the author if not already in the graph and connect it to author
        # and parent node.
        # If the comment already exists in the graph, do nothing.
        # Assumes: parent node (Submission or Comment)
        # already added to the remote graph. This will be the case if the
        # submission is added first and then the comments are added one at a
        # time in the order returned by praw's submission.comments.replace_more()
        if comment is None:
            return

        if comment.author is not None:
            user = self.get_node("User", name = comment.author.name)
            if user is None:
                user = self.add_author(comment.author)

        parent_type = "Submission" if comment.is_root else "Comment"
        parent = self.get_node(parent_type, id = comment.parent_id[3:])

        c = pn.Node("Comment", **self.scraper.get_attributes(comment, "Comment"))
        self.add(c)
        if comment.author is not None:
            posted = pn.Relationship(user, "POSTED", c)
            self.add(posted)
        if parent is not None:
            posted_on = pn.Relationship(c, "REPLY_TO", parent)
            self.add(posted_on)

        self.commit_subgraph()
        return c
