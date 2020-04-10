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
        try:
            self.id = sr.id
        except:
            self.id = -1
            return
        attrs = dict(vars(sr))
        self.id = attrs.get("id", None)
        self.name = attrs.get("display_name", None)
        self.description = attrs.get("public_description", None)
        self.num_subscribers = attrs.get("subscribers", None)
        self.created_time = attrs.get("created_utc", None)

    def __str__(self):
        return f"[Subreddit {self.id}] r/{self.name}"

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
    comments = RelatedFrom("Comment", "COMMENT_ON")
    codes = RelatedFrom("Code", "CODED")

    def __init__(self, sb):
        super().__init__()
        try:
            self.id = sb.id
        except:
            self.id = -1
            return
        attrs = dict(vars(sb))
        self.id = attrs.get("id", -1)
        self.title = attrs.get("title", None)
        self.url = attrs.get("url", None)
        self.text = attrs.get("selftext", None)
        self.score = attrs.get("score", None)
        self.upvote_ratio = attrs.get("upvote_ratio", None)
        self.link = attrs.get("permalink", None)
        self.created_time = attrs.get("created_utc", None)

    def __str__(self):
        author = [a for a in self.author][0].name
        if self.url:
            return f"[Submission {self.id}]\n {author}: {self.title} ({self.url}) \n {self.text}"
        return f"[Submission {self.id}]\n {author}: {self.title} \n {self.text}"


class Comment(GraphObject):
    __primarykey__ = "id"

    id = Property()
    text = Property()
    score = Property()
    link = Property()
    created_time = Property()
    submission = Property()
    top_level = Property()

    parent_submission = RelatedTo("Submission", "COMMENT_ON")
    parent_comment = RelatedTo("Comment", "REPLY_TO")
    author = RelatedFrom("User", "COMMENTED")
    replies = RelatedFrom("Comment", "REPLY_TO")
    codes = RelatedFrom("Code", "CODED")

    def __init__(self, c):
        super().__init__()
        try:
            self.id = c.id
        except:
            self.id = -1
            return
        attrs = dict(vars(c))
        self.id = attrs.get("id", -1)
        self.text = attrs.get("body", None)
        self.score = attrs.get("score", None)
        self.link = attrs.get("permalink", None)
        self.created_time = attrs.get("created_utc", None)
        self.submission = attrs.get("link_id", None)
        if self.submission:
            self.submission = self.submission[3:]
        self.top_level = attrs.get("link_id") == attrs.get("parent_id")

    def __str__(self):
        author = [a for a in self.author][0].name

        if self.top_level:
            ptype = "Submission"
            parent = [p for p in self.parent_submission][0]
            return f"[Comment {self.id} -> {ptype} {parent.id}] {author}: {self.text}"

        ptype = "Comment"
        parent = [p for p in self.parent_comment][0]
        return f"[Comment {self.id} -> {ptype} {parent.id} | Submission {self.submission}]\n{author}: {self.text}"



class User(GraphObject):
    __primarykey__ = "name"

    id = Property()
    name = Property()
    comment_karma = Property()
    created_time = Property()
    link_karma = Property()

    submissions = RelatedTo("Submission", "POSTED")
    comments = RelatedTo("Comment", "COMMENTED")

    def __init__(self, author):
        super().__init__()
        try:
            self.id = author.id
        except:
            self.id = -1
            return
        attrs = dict(vars(author))
        self.id = attrs.get("id", -1)
        self.name = attrs.get("name", None)
        self.comment_karma = attrs.get("comment_karma", None)
        self.link_karma = attrs.get("link_karma", None)
        self.created_time = attrs.get("created_utc", None)

    def __str__(self):
        return f"[User {self.id}] {self.name}"

class Code(GraphObject):
    __primarykey__ = "code"

    code = Property()
    description = Property()

    parent_code = RelatedFrom("Code", "SUBCODE")
    child_codes = RelatedTo("Code", "SUBCODE")
    excerpts = RelatedTo("Comment", "CODED")
    submission_excerpts = RelatedTo("Submission", "CODED")

    def __init__(self, code, description = None):
        super().__init__()
        self.code = code
        self.description = description

    def __str__(self):
        parent = [p for p in self.parent_code]
        result = ""
        if len(parent) > 0:
            result += f"{str(parent[0])}: "
        result += self.code
        if self.description:
            result += f" - {self.description}"
        return result
