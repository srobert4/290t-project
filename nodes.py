from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom

class Subreddit(GraphObject):
    __primarykey__ = "id"
    # __primarylabel__ is by default the class name. Could change this to "node" or something
    # universal so that we can merge subgraphs more easily?

    id = Property()
    name = Property()
    description = Property()
    created_time = Property()
    num_subscribers = Property()

    posts = RelatedFrom("Submission", "POSTED_ON")

    def __init__(self, sr):
        super().__init__()
        if hasattr(sr, "id"): self.id = sr.id
        if hasattr(sr, "display_name"): self.name = sr.display_name
        if hasattr(sr, "public_description"): self.description = sr.public_description
        if hasattr(sr, "created_utc"): self.created_time = sr.created_utc
        if hasattr(sr, "subscribers"): self.num_subscribers = sr.subscribers

class Submission(GraphObject):
    __primarykey__ = "id"

    id = Property()
    title = Property()
    text = Property()
    url = Property()
    score = Property()
    upvote_ratio = Property()
    link = Property()
    created_time = Property()

    subreddit = RelatedTo("Subreddit", "POSTED_ON")
    author = RelatedFrom("User", "POSTED")
    comments = RelatedFrom("Comment", "REPLY_TO")

    def __init__(self, sb):
        super().__init__()
        if hasattr(sb, "id"): self.id = sb.id
        if hasattr(sb, "title"): self.name = sb.title
        if hasattr(sb, "url"): self.num_subscribers = sb.url
        if hasattr(sb, "selftext"): self.description = sb.selftext
        if hasattr(sb, "score"): self.score = sb.score
        if hasattr(sb,"upvote_ratio"): self.upvote_ratio = sb.upvote_ratio
        if hasattr(sb, "permalink"): self.link = sb.permalink
        if hasattr(sb, "created_utc"): self.created_time = sb.created_utc

class Comment(GraphObject):
    __primarykey__ = "id"

    id = Property()
    text = Property()
    score = Property()
    link = Property()
    created_time = Property()

    parent_submission = RelatedTo("Submission", "REPLY_TO")
    parent_comment = RelatedTo("Comment", "REPLY_TO")
    author = RelatedFrom("User", "POSTED")
    replies = RelatedFrom("Comment", "REPLY_TO")

    def __init__(self, c):
        super().__init__()
        if hasattr(c, "id"): self.id = c.id
        if hasattr(c, "body"): self.text = c.body
        if hasattr(c, "score"): self.score = c.score
        if hasattr(c, "permalink"): self.link = c.permalink
        if hasattr(c, "created_utc"): self.creqated_time = c.created_utc

class User(GraphObject):
    __primarykey__ = "name"

    id = Property()
    name = Property()
    comment_karma = Property()
    created_time = Property()
    link_karma = Property()

    submissions = RelatedTo("Submission", "POSTED")
    comments = RelatedTo("Comment", "POSTED")

    def __init__(self, author):
        super().__init__()
        if hasattr(author, "id"): self.id = author.id
        if hasattr(author, "name"): self.name = author.name
        if hasattr(author, "comment_karma"): self.comment_karma = author.comment_karma
        if hasattr(author, "link_karma"): self.link_karma = author.link_karma
        if hasattr(author, "created_utc"): self.created_time = author.created_utc
