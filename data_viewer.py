# data_viewer.py
# Queries the graph for content and displays results

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
from termcolor import colored

class Data_Viewer:
    # The data viewer class allows the user to query the database and display results

    def __init__(self, graph):
        self.graph = graph
        self.rship_matcher = pn.RelationshipMatcher(self.graph)
        self.node_matcher = pn.NodeMatcher(self.graph)

    def view_submission(self, submission_id = -1, include_comments = False, submission = None):
        # Query graph for a submission and display with all comments / replies
        if not submission:
            submission = Submission.match(self.graph, submission_id).first()
        if not submission:
            print("Submission not found")
            return
        if not include_comments:
            return str(submission)

        content = [str(submission)] + [self._view_comment(comment) for comment in submission.comments]
        return "\n\n".join(content)

    def _view_comment(self, comment):
        content = [str(comment)]
        for reply in comment.replies:
            content.append(self._view_comment(reply))
        return "\n\n".join(content)

    def view_user(self, user_name):
        # Query graph for all content created by a user
        user = User.match(self.graph, user_name).first()
        if not user:
            print("User not found")
            return

        comm_sub = {}
        for comment in user.comments:
            if comment.submission in comm_sub:
                comm_sub[comment.submission].append(comment)
            else:
                comm_sub[comment.submission] = [comment]

        content = []
        for submission in user.submissions:
            content.append(str(submission))
            if submission.id in comm_sub:
                content += [str(c) for c in comm_sub.pop(submission.id)]

        for comments in comm_sub.values():
            content += [str(c) for c in comments]

        return self._construct_result_string(
            f"Content from user: {user_name}",
            content
        )

    def view_subreddit(self, subreddit_name = "", subreddit_id = None):
        # View all content on a subreddit
        if subreddit_id:
            subreddit = Subreddit.match(self.graph, subreddit_id).first()
        else:
            subreddit = node_matcher.match("Subreddit", name = subreddit_name).first()
        if not subreddit:
            print("Subreddit not found")
            return

        content = [self.view_submission(submission = submission, include_comments = True) \
                        for submission in subreddit.posts]

        return self._construct_result_string(
            f"Content on subreddit: r/{subreddit.name}",
            content
        )

    def view_coded(self, code_label):
        # View all content coded with a given code. The code label should be the label
        # of the leaf node
        code = Code.match(self.graph, code_label).first()
        if not code:
            print("Code not found")
            return

        content = []
        for content_node in code.excerpts:
            highlight = code.excerpts.get(content_node, "text")
            content += [colored(highlight, "yellow").join(str(content_node).split(highlight))]

        return self._construct_result_string(
            f"Content with code: {code_label}",
            content
        )

    def view_search(self, query):
        # View content that matches a search term
        nodes = self.graph.run(
            f"CALL db.index.fulltext.queryNodes(\"contentIndex\", \"{query}\")"
        ).to_subgraph()

        content = []
        for node in nodes.nodes:
            if node.__primarylabel__ == "Comment":
                node = Comment.match(self.graph, node["id"]).first()
            else:
                node = Submission.match(self.graph, node["id"]).first()
            content.append(str(node))

        return self._construct_result_string(
            f"Content matching search term: {query}",
            content
        )

    def _construct_result_string(self, title, content):
        result = f"[{title}]\n"
        result += "-" * (len(result) - 1) + "\n"
        result += "\n\n".join(content)
        return result
