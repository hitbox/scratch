import argparse
import configparser
import os
import random

from collections import namedtuple
from pprint import pprint

SYNTACTIC_CATEGORY = {
    1: 'noun',
    2: 'verb',
    3: 'adjective',
    4: 'adverb',
}

class LexnameRecord(
    namedtuple(
        '_LexnameRecord',
        'file_number filename syntactic_category',
    )
):
    pass


class IndexRecord(
    namedtuple(
        'IndexRecord',
        'lemma pos synset_offset'
    )
):
    """
    :param lemma:
        lower case ASCII text of word or collocation. Collocations are formed
        by joining individual words with an underscore (_ ) character.

    :param pos:
        Syntactic category: n for noun files, v for verb files, a for adjective
        files, r for adverb files.

    :param synset_offset:
        Byte offset in data.pos file of a synset containing lemma . Each
        synset_offset in the list corresponds to a different sense of lemma in
        WordNet. synset_offset is an 8 digit, zero-filled decimal integer that
        can be used with fseek(Link is external)(3)(Link is external) to read a
        synset from the data file. When passed to read_synset(3WN) along with
        the syntactic category, a data structure containing the parsed synset
        is returned.
    """


def read_lexnames(path):
    with open(path) as lexnames_file:
        for line in lexnames_file:
            items = line.strip().split('\t')
            file_number, filename, syntactic_category = items
            syntactic_category = int(syntactic_category)
            yield LexnameRecord(file_number, filename, syntactic_category)

def read_index(path):
    with open(path) as index_file:
        for line in index_file:
            if line.startswith('  '):
                # ignore starts with two spaces
                continue
            tokens = iter(line.strip().split())
            lemma = next(tokens)
            pos = next(tokens)
            # get synset_cnt for later
            synset_cnt = int(next(tokens))
            # get and ignore p_cnt and ignore that many fields
            for _ in range(int(next(tokens))):
                next(tokens)
            # ignore sense_cnt, a duplicate of synset_cnt
            next(tokens)
            # ignore tagsense_cnt
            next(tokens)
            synset_offsets = [int(next(tokens)) for _ in range(synset_cnt)]
            try:
                next(tokens)
            except StopIteration:
                # good
                pass
            else:
                raise ValueError('Not all fields consumed.')

            index_record = IndexRecord(lemma, pos, synset_offsets)
            yield index_record

def read_exception_file(path):
    with open(path) as exception_file:
        for line in exception_file:
            yield line.strip().split()

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config',
        nargs = '+',
    )
    parser.add_argument(
        '--seed',
        type = int,
    )
    args = parser.parse_args(argv)

    if args.seed:
        random.seed(args.seed)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    wordnet_config = cp['wordnet']

    root = wordnet_config['root']
    lexnames_path = os.path.join(root, 'lexnames')
    for lexname_record in read_lexnames(lexnames_path):
        pass

    extensions = ['adj', 'adv', 'noun', 'verb']

    grouped_index_records = {
        ext: list(read_index(os.path.join(root, f'index.{ext}')))
        for ext in extensions
    }

    # ext -> pos from nltk
    grouped_exceptions = {
        ext: list(read_exception_file(os.path.join(root, f'{ext}.exc')))
        for ext in extensions
    }
    for ext, excs in grouped_exceptions.items():
        for exc in excs:
            if len(exc) > 2:
                pprint([ext, exc])

if __name__ == '__main__':
    main()
