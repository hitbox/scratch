import argparse

def run():
    pass

def main(argv=None):
    """
    Two-dimensional procedural key generation.
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

if __name__ == '__main__':
    main()

# 2023-10-08
# - saw this:
#   https://www.reddit.com/r/proceduralgeneration/comments/1726sbl/procedurally_generated_keys/
# - thinking about a data structure for a key
#   - some value that you would use to match whether this key "fits" that lock.
#     just an integer? the random seed?
#   - this post's key is a 2d grid
#   - could be a randomly place set of squares but there's the consideration of
#     a physically possible key.
#   - the sticky-outty bits are called the bitting or bits.
#   - the bitting is created by the cuts.
#   - so a 2d generation procedure that produces realistic bitting or bits.
#   - or maybe 2d generation that cuts away to produce bits.
