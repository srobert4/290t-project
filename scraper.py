# scraper.py
# Currently implements a Reddit scraper, but should eventually have a base class that each
# Social media platform extends

import praw
import configparser
import time
import logging

class Reddit:

    cfg = configparser.ConfigParser()
    # ==============================
    # If you move your config file:
    # change the following line to its chosen location
    # ==============================
    cfg.read('/etc/290t-config.txt')
    cfg = cfg['reddit']

    def __init__(self):
        # Connect to Reddit
        self.cnx = praw.Reddit(client_id = self.cfg['client_id'],
                     client_secret = self.cfg['client_secret'],
                     user_agent = self.cfg['user_agent'])
        logging.info("Successfully connected to praw.Reddit instance")

    def get_subreddit(self, subreddit_name = None, source_content = None):
        if source_content is not None:
            return source_content.subreddit

        if subreddit_name is not None:
            logging.info(f"Querying Reddit API for subreddit: {subreddit_name}")
            return self.cnx.subreddit(subreddit_name)

        return None

    def get_submission(self, id = None, submission_url = None):
        # If both id and url provided, use id
        if id:
            logging.info(f"Querying Reddit API for submission: {id}")
            return self.cnx.submission(id = id)
        logging.info(f"Querying Reddit API for submission: {submission_url}")
        return self.cnx.submission(url = submission_url)

    def get_user_subs(self, user, subreddit = None, submissions = True, comments = True,
            sort = "top", time_filter = "all", limit = 100):
        logging.info(f"Querying Reddit API for user: {user}")
        user = self.cnx.redditor(name = user)
        subs = user.submissions
        comments = user.comments

        logging.info(f"Getting {limit} {sort} commments and submissions")
        if sort == "hot":
            subs = subs.hot(limit = limit)
            comments = comments.hot(limit = limit)
        elif sort == "new":
            subs = subs.new(limit = limit)
            comments = comments.new(limit = limit)
        elif sort == "top":
            subs = subs.top(time_filter, limit = limit)
            comments = comments.top(time_filter, limit = limit)
        logging.info(f"Found {len(subs)} {sort} submissions and {len(comments)} {sort} comments")

        s = set()
        if submissions:
            s = s.union({sub for sub in subs})
        if comments:
            s = s.union({c.submission for c in comments})
        if subreddit:
            s = [sub for sub in s if sub.subreddit.display_name == subreddit]

        logging.info(f"Returning {len(s)} submissions to add to graph")
        return list(s)

    def get_comment_submission(self, id = None, comment_url = None):
        if id:
            logging.info(f"Querying Reddit API for comment: {id}")
            c = self.cnx.comment(id = id)
        else:
            logging.info(f"Querying Reddit API for comment: {comment_url}")
            c = self.cnx.comment(url = comment_url)
        if hasattr(c, "submission"):
            return c.submission
        logging.info("Comment had no submission attribute. Returning None")
        return None

    def get_comments(self, submission):
        logging.info(f"Expanding comments for submission {submission.id}")
        submission.comments.replace_more(limit = None)
        return submission.comments.list()

    def get_redditor(self, name = None, source_content = None):
        if source_content is not None:
            return source_content.author

        if name is not None:
            logging.info(f"Querying Reddit API for user: {name}")
            redditor = self.cnx.redditor(name = name)
            if not redditor.is_suspended:
                return redditor
            logging.info("User {name} is suspended. Returning None")

        return None
