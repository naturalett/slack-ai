import re

class HighlightFinder:
    def __init__(self):
        self.highlight_words = []

    def set_highlight_words(self, words):
        self.highlight_words = words

    def find_highlight_words(self, text):
        pattern = r'\b\w+\b'
        matches = re.findall(pattern, text)
        return [match for match in matches if match.lower() in self.highlight_words]
