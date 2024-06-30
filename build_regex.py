import argparse
import itertools as it
import operator as op
import re

def find_common_prefix(strings):
    if not strings:
        return ""
    common_prefix = strings[0]
    for string in strings[1:]:
        while not string.startswith(common_prefix):
            common_prefix = common_prefix[:-1]
            if not common_prefix:
                return ""
    return common_prefix

def find_common_suffix(strings):
    if not strings:
        return ""
    common_suffix = strings[0]
    for string in strings[1:]:
        while not string.endswith(common_suffix):
            common_suffix = common_suffix[1:]
            if not common_suffix:
                return ""
    return common_suffix

def build_regex_for_common_prefix_suffix(strings):
    prefix = find_common_prefix(strings)
    suffix = find_common_suffix(strings)
    if prefix or suffix:
        # Escape the prefix and suffix for regex special characters
        prefix = re.escape(prefix)
        suffix = re.escape(suffix)
        return f"^{prefix}.*{suffix}$"
    # Match anything if there's no common prefix or suffix
    return ".*"

def reverse_string(string):
    return string[::-1]

def pairwise_diffs(strings):
    # assumes same length strings
    keys = ['index', '==', 'c1', 'c2']
    for s1, s2 in it.pairwise(strings):
        for index, (c1, c2) in enumerate(zip(s1, s2)):
            values = (index, int(c1 == c2), c1, c2)
            yield dict(zip(keys, values))

def unique_or(chars, if_not_unique=None):
    s = set(chars)
    if len(s) == 1:
        rv = s.pop()
    else:
        rv = if_not_unique
    return rv

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'strings',
        nargs = '+',
    )
    args = parser.parse_args(argv)

    strings = args.strings

    # assert all same length and get it
    lengths = set(map(len, strings))
    assert len(lengths) == 1
    length = lengths.pop()

    consider_indexes = list(range(length))

    common = [unique_or(chars) for chars in zip(*strings)]

    print(common)

    return

    # THINKING
    # - treat each string like a node in a graph
    # - map how to get from each node to each other node
    # - islands become regex groups
    # - find the widest and most unique parts of all strings

    buffer = list(None for _ in range(max(map(len, strings))))

    diffs = list(pairwise_diffs(strings))

    # - fill buffer at indexes where that index all have the same character

def example():
    # Example usage
    strings = ["applepie", "applecrisp", "applesauce"]
    regex_pattern = build_regex_for_common_prefix_suffix(strings)
    print(f"Regex pattern: {regex_pattern}")

    # Test the regex pattern
    test_strings = ["applepie", "applecrisp", "applesauce", "applejack", "banana"]
    compiled_regex = re.compile(regex_pattern)
    matched_strings = [s for s in test_strings if compiled_regex.match(s)]
    print(f"Matched strings: {matched_strings}")

if __name__ == '__main__':
    main()
