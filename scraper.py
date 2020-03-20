# scraper.py
# Currently implements a Reddit scraper, but should eventually have a base class that each
# Social media platform extends

import praw
import configparser

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

    def get_subreddit(self, subreddit_name = None, source_content = None):
        if source_content is not None:
            return source_content.subreddit

        if subreddit_name is not None:
            return self.cnx.subreddit(subreddit_name)

        return None

    def get_submission(self, id = None, submission_url = None):
        # If both id and url provided, use id
        if id: return self.cnx.submission(id = id)
        return self.cnx.submission(url = submission_url)

    def get_comment_submission(self, id = None, comment_url = None):
        if id:
            c = self.cnx.comment(id = id)
        else:
            c = self.cnx.comment(url = comment_urls)
        if hasattr(c, "submission"):
            return c.submission
        return None

    def get_comments(self, submission):
        submission.comments.replace_more(limit = None)
        return submission.comments.list()

    def get_redditor(self, name = None, source_content = None):
        if source_content is not None:
            return source_content.author

        if name is not None:
            return self.cnx.redditor(name = name)

        return None
