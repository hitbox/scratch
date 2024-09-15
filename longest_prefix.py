import unittest

class TestCommonPrefix(unittest.TestCase):

    def test_empty_list(self):
        self.assertEqual(longest_prefix([]), '')

    def test_empty_strings(self):
        self.assertEqual(longest_prefix(['', '', '']), '')

    def test_nothing_common(self):
        strings = ['a', 'b', 'c']
        self.assertEqual(longest_prefix(strings), '')

    def test_longest_prefix(self):
        strings = [
            'aaabbbccc',
            'aaadddeee',
            'aaafffggg',
        ]
        self.assertEqual(longest_prefix(strings), 'aaa')

    def test_exactly(self):
        strings = [
            'string',
            'string',
            'string',
        ]
        self.assertEqual(longest_prefix(strings), 'string')


def longest_prefix(strings):
    """
    Find the longest string that is a prefix of all the strings.
    """
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings:
        if len(s) < len(prefix):
            prefix = prefix[:len(s)]
        if not prefix:
            return ""
        for i in range(len(prefix)):
            if prefix[i] != s[i]:
                prefix = prefix[:i]
                break
    return prefix

# 2024-09-15 Sun.
# Found here:
# https://github.com/nedbat/cog/blob/main/cogapp/whiteutils.py
# Wanted to look at this. Thought `zip` should be in here.
# On second thought we need the index to slice.
