import argparse

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('start', type=int)
    parser.add_argument('--reach', type=int, default='1')
    args = parser.parse_args(argv)

    n = args.start
    print(f'{n=}')
    while n != args.reach:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3*n + 1
        print(f'{n=}')

if __name__ == '__main__':
    main()
