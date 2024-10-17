import argparse

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    for n in range(1000):
        is_even1 = (n % 2 == 0)
        # xor increments by one if even, otherwise decrements.
        is_even2 = (n ^ 1) == (n + 1)
        assert is_even1 == is_even2, n

if __name__ == '__main__':
    main()
