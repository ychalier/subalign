import itertools

class WordList(list):

    def __init__(self):
        list.__init__(self)
        self.cursor = 0

    def align(self, sub, threshold=10):
        tokens = sub.tokenize()
        for length in range(len(tokens), 0, -1):
            for combination in itertools.combinations(tokens, length):
                list_cursor = self.cursor
                tokens_cursor = 0
                matches = []
                while list_cursor < len(self):
                    if tokens_cursor == len(combination):
                        break
                    if tokens_cursor > 0 and list_cursor - matches[-1] > threshold:
                        list_cursor = matches.pop() + 1
                        tokens_cursor -= 1
                    if self[list_cursor].text == combination[tokens_cursor]:
                        tokens_cursor += 1
                        matches.append(list_cursor)
                    list_cursor += 1
                if len(matches) == len(combination):
                    self.cursor = list_cursor
                    return matches
