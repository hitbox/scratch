import argparse

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

if __name__ == '__main__':
    main()

# 2023-12-06
# - https://mathspp.com/blog/divmod-for-unit-conversions
# - article about divmod
# - mentions meta tic-tac-toe
# - want to write it
# - just guessing:
#   - players take turns placing their symbol
#   - when one of the inner games is won, that player has taken that meta-board
#     square
