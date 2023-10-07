from itertools import combinations
import os

def is_valid(phrase):
    words = phrase.split(" ")
    return len(words) == len(set(words))

def is_valid2(phrase):
    words = phrase.split(" ")
    if any(True for word1, word2 in combinations(words, 2)
                if sorted(word1) == sorted(word2)):
        return False
    return is_valid(phrase)

def tests():
    assert is_valid("aa bb cc dd ee")
    assert not is_valid("aa bb cc dd aa")
    assert is_valid("aa bb cc dd aaa")

    assert is_valid2("abcde fghij")
    assert not is_valid2("abcde xyz ecdab")
    assert is_valid2("a ab abc abd abf abj")
    assert is_valid2("iiii oiii ooii oooi oooo")
    assert not is_valid2("oiii ioii iioi iiio")

def get_input_file():
    return open(os.path.join(os.path.dirname(__file__), "input.txt"))

def count_valid(validator):
    with get_input_file() as input_file:
        n = 0
        for phrase in input_file.readlines():
            if validator(phrase.strip()):
                n += 1
    return n

def main():
    tests()
    print("part 1: %s" % (count_valid(is_valid), ))
    print("part 2: %s" % (count_valid(is_valid2), ))

if __name__ == "__main__":
    main()
