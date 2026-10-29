import argparse
import random

from itertools import zip_longest

class CodeMaker:

    def __init__(self, length=4):
        self.length = length

    def make_code(self, symbols):
        return random.sample(symbols, self.length)

    def get_feedback(self, code, guess):
        exists = set(code).intersection(guess)
        positioned = []
        for g, c in zip(guess, code):
            if g == c:
                positioned.append(c)

        feedback = {
            'exists': len(exists),
            'positioned': len(positioned)
        }
        return feedback


class CodeBreaker:

    def __init__(self, symbols, code_length):
        self.symbols = symbols
        self.code_length = code_length

    def guess_code(self):
        """
        Return a single guess at the secret code.
        """


class HumanCodeBreaker(CodeBreaker):

    def guess_code(self, formatter=None):
        if formatter is None:
            def formatter(code):
                return ''.join('_' if peg is None else peg for peg in code)

        while True:
            stdin = input('> ')

            if len(stdin) < self.code_length:
                print(f'Reponse smaller than code length, {self.code_length}')
            else:
                for position, char in enumerate(stdin):
                    if char not in self.symbols + ['_', ' ']:
                        print(f'Invalid character at {position}: {char}')
                        break
                else:
                    # validated
                    return list(stdin)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--symbols',
        type = list,
        default = 'rbgyop',
        help = 'The set of possible symbols for a code.',
    )
    parser.add_argument(
        '--code-length',
        type = int,
        default = 4,
    )
    parser.add_argument(
        '--cheat',
        action = 'store_true'
    )
    args = parser.parse_args(argv)

    code_maker = CodeMaker(length=args.code_length)
    code = code_maker.make_code(args.symbols)
    if args.cheat:
        print(code)

    code_breaker = HumanCodeBreaker(symbols=args.symbols, code_length=args.code_length)
    
    while True:
        guess = code_breaker.guess_code()
        if guess == code:
            print('Code is broken!')
            break

        feedback = code_maker.get_feedback(code, guess)
        print(feedback)

if __name__ == '__main__':
    main()
