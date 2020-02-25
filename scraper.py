# scraper.py
# Currently implements a Reddit scraper, but should eventually have a base class that each
# Social media platform extends

import praw

class Reddit:
    
    content_attrs = {
        "submission" : ["id", "text", "url", "score", "upvote_ratio"],
        "author" : ["id","name","comment_karma","created","link_karma"],
        "subreddit" : ["id", "display_name", "descr", "created", "subscribers"],
        "comment" : ["id", 'text', "score", "url"]
    }
    
    def __init__(self):
        # Connect to Reddit
        self.cnx = praw.Reddit(client_id='8bgMudNSu0bC6Q',
                     client_secret='4evDbSmLfVBsuV6X8hoX8XHhaCA',
                     user_agent='testscript by /u/catlady900')
     
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
        return self._get_attr_dict(obj, content_attrs[obj_type.to_lower()])
    
     
    def get_subreddit(subreddit_name = None, source_content = None):
        if source_content is not None:
            return source_content.subreddit
        
        if subreddit_name is not None:
            return self.cnx.subreddit(subreddit_name)
        
        return None
    
    def get_submission(submission_url):
        return self.cnx.submission(url = submission_url)
     
    def get_comments(submission):
        submission.comments.replace_more(limit = None)
        return submission.comments.list()
    
    def get_author(author_name = None, source_content = None):
        if source_content is not None:
            return source_content.author
        
        if author_name is not None:
            return self.cnx.redditor(author_name)
        
        return None