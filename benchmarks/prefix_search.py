import argparse
import timeit

from bisect import bisect_left

def prefix_search_loop(wordlist, prefix):
    for word in wordlist:
        if word.startswith(prefix):
            yield word

def prefix_search_bisect(wordlist, prefix):
    try:
        index = bisect_left(wordlist, prefix)
    except IndexError:
        pass
    else:
        while wordlist[index].startswith(prefix):
            yield wordlist[index]
            index += 1

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix_and_words', nargs='+')
    parser.add_argument('--func', choices=['loop', 'bisect'], default='loop')
    args = parser.parse_args(argv)

    if len(args.prefix_and_words) < 2:
        parser.error('two or more arguments are required')

    prefix, *wordlist = args.prefix_and_words

    if args.func == 'loop':
        func = prefix_search_loop
    elif args.func == 'bisect':
        func = prefix_search_bisect

    print(func.__name__)
    for word in func(wordlist, prefix):
        print(word)

if __name__ == '__main__':
    main()

# https://martinheinz.dev/blog/106
