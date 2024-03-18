import argparse
import collections
import random
import string
import textwrap

from itertools import tee

def _prewise(iterables, n, silent=False):
    """
    Produce n streams from iterables of streams, with offsets.
    """
    streams = tee(iterables, n)
    for i, stream in enumerate(streams):
        for _ in range(i):
            try:
                next(stream)
            except StopIteration:
                if not silent:
                    raise
    return streams

def nwise(iterables, n=2, fillvalue=None, silent=False):
    """
    yield n-wise
    """
    streams = _prewise(iterables, n, silent=silent)
    return zip(*streams)

def wordsgen(path):
    with open(path) as fp:
        text = fp.read()
    words = ( word.strip(string.punctuation)
              for line in text.splitlines()
              if line
              for word in line.split()
              if word and not word.isupper() )
    return words

def markov_text(path, select, above):
    """
    :param path: path to source text.
    :param select: number of words to select, at most.
    :param above: select words with more than this number of related words.
    """
    words = wordsgen(path)
    words1, words2 = tee(words)

    # indexed unique words
    index_word = dict(enumerate(set(words1)))
    # words back to their index
    word_index = dict(zip(index_word.values(), index_word.keys()))

    # initialize matrix
    n = len(index_word)
    matrix = [[0]*n]*n

    # count relationships
    for edge in nwise(words2):
        lword, rword = edge
        lindex = word_index[lword]
        rindex = word_index[rword]
        matrix[lindex][rindex] += 1

    # build list of, at most, select words
    # select istitle first and then only islower afterwards.
    istitle_words = [index for index, word in index_word.items() if word.istitle()]
    lindex = random.choice(istitle_words)
    lword = index_word[lindex]
    selected = [lword]
    #
    islower_index = {index for index, word in index_word.items() if word.islower()}
    for _ in range(select):
        # list of related indexes where the index appears as many times as it
        # was counted as an edge above.
        available = [ index for index, appears in enumerate(matrix[lindex])
                            if appears > above and index in islower_index
                            for _ in range(appears) ]
        if not available:
            break
        rindex = random.choice(available)
        rword = index_word[rindex]
        selected.append(rword)
        lindex = rindex
    return selected

def main(argv=None):
    """
    Markov chain sentences.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('--select', type=int, default=10,
            help='Maximum number of words to select. Default: %(default)s')
    parser.add_argument('--above', type=int, default=0)
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args(argv)

    selected = markov_text(args.source, args.select, args.above)
    if not args.silent:
        print('\n'.join(textwrap.wrap(' '.join(selected))))

if __name__ == '__main__':
    main()

# 2023-11-12
# - renew interest reading:
#   https://benhoyt.com/writings/markov-chain/
# - wondering how well I implemented this long ago.
