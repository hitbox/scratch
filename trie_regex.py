import argparse
import logging
import re
import unittest

class TestTrieRegex(unittest.TestCase):

    def check(self, words, pattern):
        self.assertEqual(build_regex_from_list(words), pattern)
        for word in words:
            self.assertTrue(re.match(pattern, word))

    def test_empty_string(self):
        self.check([''], '^$')

    def test_single_word(self):
        self.check(['cat'], '^cat$')

    def test_short_same_length(self):
        self.check(['cat', 'car', 'can'], '^ca(?:t|r|n)$')

    def test_multi_char_end_of_word(self):
        self.check(['dow', 'dowel'], '^dow(?:el)?$')
        self.check(['car', 'cartoon'], '^car(?:toon)?$')

    def test_highly_nested(self):
        words = ['dan', 'dog', 'door', 'dock', 'dope', 'dork', 'dorm', 'dow', 'dowel']
        pattern = '^d(?:an|o(?:g|or|ck|pe|r(?:k|m)|w(?:el)?))$'
        self.check(words, pattern)


class TrieNode:

    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """
        Walk down from root node adding the characters of `word` as nodes.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True


def trie_to_regex(node):
    logger = logging.getLogger('trie_to_regex.trie_to_regex')
    logger.debug(
        'node=%r, node.children=%r, node.is_end_of_word=%r',
        node, node.children.keys(), node.is_end_of_word)

    if not node.children:
        logger.debug('no children')
        return ''

    alternatives = []
    for char, child_node in node.children.items():
        sub_regex = trie_to_regex(child_node)
        if sub_regex:
            if child_node.is_end_of_word and not sub_regex.endswith('?'):
                sub_regex = '(?:' + sub_regex + ')?'
            alternatives.append(char + sub_regex)
        else:
            # no children in child node
            alternatives.append(char)
    logger.debug('alternatives=%r', alternatives)

    if len(alternatives) == 1:
        return alternatives[0]
    else:
        # non-capturing group matching any of the alternatives
        return '(?:' + '|'.join(alternatives) + ')'

def build_regex_from_list(strings):
    trie = Trie()
    for string in strings:
        trie.insert(string)

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
    parser.add_argument(
        '--logging',
        choices = [name.lower() for name in logging._nameToLevel],
        help = 'Debugging output.',
    )
    args = parser.parse_args(argv)

    if args.logging:
        logging.basicConfig(level=args.logging.upper())

    strings = sorted(args.strings)
    pattern = build_regex_from_list(strings)
    logger = logging.getLogger('trie_regex')
    logger.debug('pattern=%r', pattern)
    regex = re.compile(pattern)
    for string in strings:
        assert regex.match(string), f'{string=} does not match.'
    logger.debug('regex confirmed')

if __name__ == '__main__':
    main()
