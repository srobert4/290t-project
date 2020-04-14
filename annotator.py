# annotator.py
# Adds codes to content

import py2neo as pn
from nodes import Submission, Subreddit, Comment, User, Code
import logging

class Annotator:
    # The annotator class is responsible for adding annotations to content
    logging.basicConfig(filename='annotator.log', level=logging.INFO)

    def __init__(self, graph):
        self.graph = graph
        self.rship_matcher = pn.RelationshipMatcher(self.graph)
        self.node_matcher = pn.NodeMatcher(self.graph)

    def annotate(self, code, content_id, content_type, content):
        # code: an annotation in the format code1: subcode; code2: subcode
        # content_id: the Reddit id of the content node
        # content_type: Comment or Submission
        # content: the substring of the content to be annotated
        if content_type == "Submission":
            content_node = Submission.match(self.graph, content_id).first()
        else:
            content_node = Comment.match(self.graph, content_id).first()

        codes = self._parse_code(code)
        for code_levels in codes:
            self._add_codes(code_levels, content_node, content)

    def get_code(self, code_label):
        # return Code object with code_label
        return Code.match(self.graph, code_label).first()

    def update_code(self, code_label = None,
                    description = None, new_label = None, code = None):
        # code: Code object to update (or match by label if None)
        # code_label: code_label to match if Code is None
        # new_label: updated label
        # description: updated description
        if not code:
            code = self.get_code(code_label)
        if not code:
            print("Code not found")
            return

        if new_label:
            code.code = new_label
        if description:
            code.description = description
        self.graph.push(code)

    def delete_code(self, code_label = None, code = None, confirm = True):
        # Delete Code object (if not None) or code matched by code_label (if Code is None)
        # confirm: whether to ask the user to confirm before deleting Code node (default True)
        # If deleting the code will leave any dangling Code nodes with no children, those will
        # also be deleted.
        # i.e. parent codes are recursively deleted if they have only one child and that child will be deleted.
        if not code:
            code = self.get_code(code_label)
        if not code:
            print("Code not found")
            return
        if confirm:
            if input(f"Delete code: {code.code}? Type 'Y' to confirm: ").lower() != "y":
                print("Cancelled")
                return

        for parent in code.parent_code:
            if len(parent.child_codes) == 1:
                self.delete_code(code = parent, confirm = False)

        print(f"Deleting code {code.code}")
        self.graph.delete(code)


    def _parse_code(self, code):
        # input: code1: subcode1; code2: subcode2
        # output: list of lists. for each list: ordered from highest level to lowest level code
        codes = code.split(";")
        return [c.split(":") for c in codes]

    def _add_codes(self, code_levels, content_node, content):
        # recursive wrapper
        code = self._add_code(code_levels.pop(0).strip(), code_levels, content_node, content)
        self.graph.push(code)

    def _add_code(self, code_label, children, content_node, content):
        # recursively add code with code_label, then children.
        # leaf node is connected to the content_node and this relationship
        # is labelled with content
        code = self.get_code(code_label)
        if not code:
            code = Code(code_label)
        if len(children) == 0:
            self._add_content(code, content_node, content)
        else:
            child = self._add_code(children.pop(0).strip(), children, content_node, content)
            child.parent_code.add(code)
            self.graph.push(child)
        return code

    def _add_content(self, code, content_node, content):
        # connect leaf code node to content and label relationship with substring to code (content)
        if content_node.__primarylabel__ == "Submission":
            code.submission_excerpts.add(content_node, text = content)
        else:
            code.excerpts.add(content_node, text = content)
