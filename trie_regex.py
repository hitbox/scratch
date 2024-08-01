import argparse
import logging

class TrieNode:

    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True


def trie_to_regex(node):
    logger = logging.getLogger('trie_to_regex')
    if not node.children:
        logger.info('no children')
        return ''

    alternatives = []
    for char, child in node.children.items():
        sub_regex = trie_to_regex(child)
        if child.is_end_of_word:
            if sub_regex:
                alternatives.append(char + sub_regex + '?')
            else:
                alternatives.append(char)
        else:
            alternatives.append(char + sub_regex)
        logger.info('%r', alternatives)

    if len(alternatives) == 1:
        return alternatives[0]
    else:
        return '(?:' + '|'.join(alternatives) + ')'

def build_regex_from_list(strings):
    logger = logging.getLogger('trie_to_regex')
    trie = Trie()
    for string in strings:
        trie.insert(string)

    logger.info('%r', trie.root.children)
    regex = trie_to_regex(trie.root)
    return '^' + regex + '$'

def example():
    # Example Usage
    strings = ['cat', 'car', 'cart', 'dog', 'dot']
    regex_pattern = build_regex_from_list(strings)
    print(f"Regex pattern: {regex_pattern}")

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'strings',
        nargs = '+',
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    pattern = build_regex_from_list(args.strings)
    print(pattern)

if __name__ == '__main__':
    main()
