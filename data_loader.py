# data_loader.py
# Loads data to graph

import py2neo as pn
import Reddit

class Data_Loader:
    
    def __init__(self, scraper):
        self.graph = pn.Graph(auth=("neo4j", "paBa%Wp36^"))
        self.subgraph = pn.Subgraph()
        self.scraper = Reddit()
        # TODO: add constraints
        self.graph.schema.create_uniqueness_constraint("User", "id")
        self.graph.schema.create_uniqueness_constraint("Submission", "id")
        self.graph.schema.create_uniqueness_constraint("Comment", "id")
        self.graph.schema.create_uniqueness_constraint("Subreddit", "id")
    
    def clear_graph(self):
        self.graph.delete_all()
   
    def commit_subgraph(self):
        txn = self.graph.begin()
        txn.create(self.subgraph)
        txn.commit()
        self.subgraph = pn.Subgraph
       
    def get_node(self, node_type, kwargs):
        nodes = self.graph.nodes.match(node_type, **kwargs)
        if len(nodes) > 0:
            return nodes.first()
        nodes = self.subgraph.nodes.match(node_type, **kwargs)
        if len(nodes) > 0:
            return nodes.first()
        return None
        
    def load_submissions(submission_urls):
        for submission in submission_urls:
            sub = self.scraper.get_submission(submission)
            if sub is not None:
                self.add_submission(sub)
        self.commit_subgraph()
            
    def add_submission(self, submission):
        # If submission exists, return
        sb = self.get_node("Submission", id=submission.id)
        if sb is not None: return sb
        
        # Add the subreddit if not already added to subgraph
        subreddit = self.add_subreddit(self.scraper.get_subreddit(source_content = submission))
        
        # Add the author if not already added to subgraph
        author = self.add_author(self.scraper.get_author(source_content = submission))
        
        # Add the submission to subgraph
        sb = pn.Node("Submission", **self.scraper.get_attributes(submission, "Submission"))
        self.subgraph.add(sb)
        
        # Connect submission to author and subreddit
        if author is not None:
            posted = pn.Relationship(author, "POSTED", sb)
            self.subgraph.add(posted)
        
        posted_on = pn.Relationship(sb, "POSTED_ON", subreddit)
        self.subgraph.add(posted_on)
        
        # Add the comments to the subgraph
        for comment in self.scraper.get_comments(submission):
            c = self.add_comment(comment)
        
        return sb
    
    def add_subreddit(self, sr):
        if sr is None: return None
        subreddit = self.get_node("Subreddit", id=sr.id) # TODO: check subgraph not graph
        if subreddit is not None:
            return subreddit
        subreddit = pn.Node("Subreddit", **self.scraper.get_attributes(sr, "Subreddit"))
        self.subgraph.add(subreddit)
        return subreddit

    def add_author(self, author):
        if author is None: return None
        user = self.get_node("User", name= author.name) # TODO: check subgraph not graph
        if user: return user
        user = pn.Node("User", **self.scraper.get_attributes(author, "author"))
        self.subgraph.add(user)
        return user

    def add_comment(self, comment):
        if comment is None:
            return
        
        if comment.author is not None:
            user = self.get_node("User", name = comment.author.name) # TODO: check subgraph not graph
            if user is None:
                user = self.add_author(comment.author)

        parent_type = "Submission" if comment.is_root else "Comment"
        parent = self.get_node(parent_type, id = comment.parent.id) # TODO: check subgraph not graph
               
        c = pn.Node("Comment", **scraper.get_attributes(comment, "Comment"))
        self.subgraph.add(c)
        if comment.author is not None:
            posted = pn.Relationship(user, "POSTED", c)
            self.subgraph.add(posted)
        if parent is not None:
            posted_on = pn.Relationship(c, "REPLY_TO", parent)
            self.subgraph.add(posted_on)
            
        return c
    