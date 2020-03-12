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

    content_attrs = {
        "submission" : ["id", "title", "selftext", "url", "score", "upvote_ratio", "permalink", "created_utc"],
        "author" : ["id","name","comment_karma","created_utc","link_karma"],
        "subreddit" : ["id", "display_name", "public_description", "created_utc", "subscribers"],
        "comment" : ["id", "body", "score", "permalink", "created_utc"]
    }

    def __init__(self):
        # Connect to Reddit
        self.cnx = praw.Reddit(client_id = self.cfg['client_id'],
                     client_secret = self.cfg['client_secret'],
                     user_agent = self.cfg['user_agent'])

    def _get_attr_dict(self, obj, atts):
        # Returns a dictionary of attributes of obj
        # - obj: an object with some subset of the attributes in atts
        # - atts: a list of strings with the names of the attributes
        # returns: dict att -> obj.att
        if obj is None: return None
        attrs = dict()
        for v in atts:
            if hasattr(obj, v):
                attrs[v] = getattr(obj, v)
        return attrs


    def get_attributes(self, obj, obj_type):
        return self._get_attr_dict(obj, self.content_attrs[obj_type.lower()])


    def get_subreddit(self, subreddit_name = None, source_content = None):
        if source_content is not None:
            return source_content.subreddit

        if subreddit_name is not None:
            return self.cnx.subreddit(subreddit_name)

        return None

    def get_submission(self, submission_url):
        return self.cnx.submission(url = submission_url)

    def get_comments(self, submission):
        submission.comments.replace_more(limit = None)
        return submission.comments.list()

    def get_author(self, author_name = None, source_content = None):
        if source_content is not None:
            return source_content.author

        if author_name is not None:
            return self.cnx.redditor(author_name)

        return None
