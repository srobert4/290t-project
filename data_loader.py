# data_loader.py
# Loads data to graph

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User
from scraper import Reddit
import time
import logging

class Data_Loader:
    # The data loader class is responsible for using a scraper to get data from
    # Reddit and adding it to the Neo4j database
    logging.basicConfig(filename='data_loader.log', level=logging.INFO)

    def __init__(self, graph):
        self.graph = graph
        self.subgraph = None
        self.scraper = Reddit()

        # Only add uniqueness constraints once
        if len(self.graph.schema.get_uniqueness_constraints("User")) == 0:
            logging.info("Adding uniqueness constraints to graph")
            self.graph.schema.create_uniqueness_constraint("User", "id")
            self.graph.schema.create_uniqueness_constraint("Submission", "id")
            self.graph.schema.create_uniqueness_constraint("Comment", "id")
            self.graph.schema.create_uniqueness_constraint("Subreddit", "id")

            logging.info("Adding text indices to graph")
            self.graph.evaluate(
                "CALL db.index.fulltext.createNodeIndex(\"contentIndex\",[\"Submission\", \"Comment\"],[\"title\", \"text\"])"
            )
            self.graph.evaluate(
                "CALL db.index.fulltext.createNodeIndex(\"codeIndex\",[\"Code\"],[\"code\"])"
            )
            self.graph.evaluate(
                "CALL db.index.fulltext.createRelationshipIndex(\"excerptIndex\",[\"CODED\"],[\"excerpts\", \"submission_excerpts\"])"
            )

    def clear_graph(self):
        # delete all nodes in the graph
        self.graph.delete_all()

    def load_submissions(self, submission_urls):
        # Given a list of Reddit submission urls, add all of the submissions
        # to the graph, including authors, subreddits and comments
        for submission in submission_urls:
            print(f"Adding submission: {submission}")
            sub = self.scraper.get_submission(submission_url = submission)
            if sub is not None:
                s = self.add_submission(sub)

    def load_from_comment(self, comment_urls):
        for url in comment_urls:
            submission = self.scraper.get_comment_submission(comment_url = url)
            if submission is not None:
                self.add_submission(submission)

    def load_by_subreddit(self, subreddit_name,
                        time_filter = None, n_popular = None,
                        n_recent = None, n_sample = None,
                        controversial = None, search_query = None, search_limit = 1):
        self._load_by_subreddit_or_user(
            subreddit_name = subreddit_name, time_filter = time_filter, n_popular = n_popular,
            n_recent = n_recent, n_sample = n_sample, controversial = controversial,
            search_query = search_query, search_limit = search_limit
        )

    def load_by_user(self, user_name,
                    time_filter = None, n_popular = None,
                    n_recent = None,n_sample = None,
                    controversial = None, search_query = None, search_limit = 1):
        self._load_by_subreddit_or_user(
            user_name = user_name, time_filter = time_filter,
            n_popular = n_popular, n_recent = n_recent,
            n_sample = n_sample, controversial = controversial,
            search_query = search_query, search_limit = search_limit
        )

    def load_by_user_and_subreddit(self, user_name, subreddit_name, submissions = True, comments = True,
                sort = "top", time_filter = "all", limit = 100):
        user_subs = self.scraper.get_user_subs(user_name, subreddit_name, submissions, comments,
            sort, time_filter, limit)

        for submission in user_subs:
            self.add_submission(submission)

    def _load_by_subreddit_or_user(self, subreddit_name = None, user_name = None,
        time_filter = None, n_popular = None, n_recent = None,
        n_sample = None, controversial = None, search_query = None, search_limit = 1):
        if subreddit_name:
            obj = self.scraper.get_subreddit(subreddit_name = subreddit_name)
        elif user_name:
            obj = self.scraper.get_redditor(name = user_name)
        else:
            return

        if search_query:
            if time_filter is None:
                time_filter = "all"
            submissions = obj.search(query = search_query, time_filter = time_filter)
        elif time_filter:
            submissions = obj.top(time_filter = time_filter)
        elif n_popular:
            submissions = obj.hot(limit = n_popular)
        elif n_recent:
            submissions = obj.new(limit = n_recent)
        elif n_sample:
            submissions = obj.random(limit = n_sample)
        elif controversial:
            submissions = obj.controversial(time_filter = controversial)
        else:
            return

        n_added = 0
        for submission in submissions:
            self.add_submission(submission)
            n_added = n_added + 1
            if search_query and search_limit == n_added:
                return

    def add_submission(self, sb):
        # submission: praw Submission object to add to remote graph
        # If submission is not already in the remote graph, add it along
        # with the author and subreddit if not already in the graph, as well
        # as all its comments
        # If the submission already exists in the graph, do nothing.

        # If submission exists, return node
        logging.info(f"Adding submission ({sb.id}): {sb.permalink}")
        tic = time.perf_counter()
        submission = Submission.match(self.graph, sb.id).first()
        if submission is not None:
            toc = time.perf_counter()
            print("Submission already in graph")
            logging.info("Submission already in graph")
            return submission

        # Add the submission to subgraph
        fetch = sb.title # fetch non-Lazy version
        submission = Submission(sb)
        if submission.id == -1:
            logging.info("Bad submission added to the graph")
            return None

        # Add the subreddit if not already added to subgraph
        attrs = dict(vars(sb))
        if attrs.get("subreddit", False) and sb.subreddit:
            subreddit = self.add_subreddit(sb.subreddit)
            submission.subreddit.add(subreddit)

        # Add the author if not already added to subgraph
        if attrs.get("author", False) and sb.author:
            author = self.add_author(sb.author)
            submission.author.add(author)

        self.graph.push(submission)

        # Add the comments to the subgraph
        comments =  self.scraper.get_comments(sb)
        logging.info(f"Adding {len(comments)} comments...")
        for comment in comments:
            self.add_comment(comment)
        toc = time.perf_counter()
        print(f"Submission {submission.id} and {len(comments)} comments added in {toc - tic:0.4f}s")
        return submission

    def add_subreddit(self, sr):
        # sr: praw Subreddit object
        # If subreddit exists in remote graph: return corresponding Node
        # Else: add subreddit to local subgraph and return new Node
        if sr is None: return None
        subreddit = Subreddit.match(self.graph, sr.id).first()
        if subreddit is not None:
            logging.info(f"Subreddit {subreddit.name} already in graph")
            return subreddit

        fetch = sr.display_name # non-Lazy version
        logging.info(f"Adding subreddit: r/{fetch}")
        subreddit = Subreddit(sr)
        if subreddit.id != -1:
            self.graph.push(subreddit)
            return subreddit
        return None

    def add_author(self, author):
        # author: praw Redditor object
        # If user exists in remote graph: return corresponding Node
        # Else: add user to local subgraph and return new Node
        if author is None: return None
        user = User.match(self.graph, author.name).first()
        if user:
            logging.info(f"User {user.name} already in graph")
            return user

        logging.info(f"Adding user: {author.name}")
        user = User(author)
        if user.id != -1:
            self.graph.push(user)
            return user
        return None

    def add_comment(self, c):
        # comment: praw comment object to add to remote graph
        # If comment is not already in the remote graph, add it along
        # with the author if not already in the graph and connect it to author
        # and parent node.
        # If the comment already exists in the graph, do nothing.
        # Assumes: parent node (Submission or Comment)
        # already added to the remote graph. This will be the case if the
        # submission is added first and then the comments are added one at a
        # time in the order returned by praw's submission.comments.replace_more()
        if c is None:
            return
        comment = Comment.match(self.graph, c.id).first()
        if comment:
            logging.info(f"Comment ({comment.id}) already in graph")
            return comment

        fetch = c.body # Non-lazy version
        comment = Comment(c)
        if comment.id != -1:
            self.graph.push(comment)


        attrs = dict(vars(c))
        # Add the author if not already added to subgraph
        if attrs.get("author", False) and c.author:
            user = User.match(self.graph, c.author.name).first()
            if user is None:
                user = self.add_author(c.author)
            if user.id != -1:
                user.comments.add(comment)
                self.graph.push(user)

        if attrs.get("parent_id", False) and c.parent_id:
            if c.is_root:
                parent = Submission.match(self.graph, c.parent_id[3:]).first()
                parent.comments.add(comment)
            else:
                parent = Comment.match(self.graph, c.parent_id[3:]).first()
                parent.replies.add(comment)
            self.graph.push(parent)

        return comment
