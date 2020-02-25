# data_loader.py
# Loads data to graph

import py2neo as pn
import Reddit

class Data_Loader:
    
    def __init__(self, scraper):
        self.graph = pn.Graph(auth=("neo4j", "paBa%Wp36^"))
        self.subgraph = None
        self.scraper = Reddit()
        # TODO: add constraints
    
    def clear_graph(self):
        pass
    
    def commit_subgraph(self):
        txn = self.graph.begin()
        txn.create(self.subgraph)
        txn.commit()
    
    def load_submissions(submission_urls):
        for submission in submission_urls:
            sub = self.scraper.get_submission(submission)
            if sub is not None:
                self.add_submission(sub)
        self.commit_subgraph()
            
    def add_submission(self, submission):
        # If submission exists, return
        if len(graph.nodes.match("Submission", id=submission.id)) > 0: # TODO: check subgraph not graph
            return
        
        # Add the subreddit if not already added to subgraph
        subreddit = self.add_subreddit(self.scraper.get_subreddit(source_content = submission))
        
        # Add the author if not already added to subgraph
        author = self.add_author(self.scraper.get_author(source_content = submission))
        
        # Add the submission to subgraph
        sb = pn.Node("Submission", **self.scraper.get_attributes(submission, "Submission"))
        # Connect submission to author and subreddit
        if author is not None:
            posted = pn.Relationship(author, "POSTED", sb)
        else:
            posted = None
        posted_on = pn.Relationship(sb, "POSTED_ON", subreddit)
        
        # Add the comments to the subgraph
        for comment in self.scraper.get_comments(submission):
            c = self.add_comment(comment)
        
        return sb, posted, posted_on
    
    def add_subreddit(self, sr):
        if sr is None: return None
        srs = graph.nodes.match("Subreddit", id=sr.id) # TODO: check subgraph not graph
        if len(srs) > 0: return srs.first()
        subreddit = pn.Node("Subreddit", **self.scraper.get_attributes(sr, "Subreddit"))
        return subreddit

    def add_author(self, author):
        if author is None: return None
        usrs = graph.nodes.match("User", name= author.name) # TODO: check subgraph not graph
        if len(usrs) > 0: return usrs.first()
        user = pn.Node("User", **self.scraper.get_attributes(author, "author"))
        return user

    def add_comment(self, comment):
        if comment is None:
            return
        if len(graph.nodes.match("Comment", id = comment.id)) > 0: # TODO: check subgraph not graph
            return

        if comment.author is not None:
            user = graph.nodes.match("User", name = comment.author.name) # TODO: check subgraph not graph
            if len(user) == 0:
                user = self.add_author(comment.author)
            else:
                user = user.first()

        parent_type = "Submission" if comment.is_root else "Comment"
        parent = graph.nodes.match(parent_type, id = comment.parent.id) # TODO: check subgraph not graph
               
        c = pn.Node("Comment", **scraper.get_attributes(comment, "Comment"))
        if comment.author is not None:
            posted = pn.Relationship(user, "POSTED", c)
        else: 
            posted = None
        if parent is not None:
            posted_on = pn.Relationship(c, "REPLY_TO", parent)
        else:
            posted_on = None
            
        return c, posted, posted_on
    