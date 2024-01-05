import argparse
import datetime
import math
import re
import string
import urllib.request

from collections import Counter

GMTFMT = '%a, %d %b %Y %H:%M:%S GMT'

unwanted_re = re.compile(f'[“”{string.punctuation}]')

def download_catalog(url):
    with urllib.request.urlopen(url) as catalog_file:
        last_modified = datetime.datetime.strptime(
            catalog_file.headers['last-modified'],
            GMTFMT
        )
        print(last_modified)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=argparse.FileType())
    args = parser.parse_args(argv)

    with args.source as source_file:
        text = source_file.read()
        text = unwanted_re.sub('', text)
        words = filter(str.islower, text.split())
        counts = Counter(words)
        probabilities = {word: count/len(counts) for word, count in counts.items()}
        surprisals = {word: math.log(prob) for word, prob in probabilities.items()}
        sorted_surprisals = sorted(surprisals, key=surprisals.__getitem__)
        print(sorted_surprisals[:10])
        print(sorted_surprisals[-10:])

if __name__ == '__main__':
    main()

# TODO
# - configparser config
# - check file at url for newer than already downloaded
# - download one author
# - save to cache
# - download top 10 by rating or something if that is available
# - predictive text engine from source
# - https://www.gutenberg.org/cache/epub/feeds/
# - https://jamesg.blog/2023/12/15/auto-write/
# - /home/hitbox/repos/reference/capjamesg/pysurprisal/pysurprisal/core.py
