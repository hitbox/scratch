import fileinput

def main():
    for line in fileinput.input():
        print(line, end='')

if __name__ == '__main__':
    main()

# 2023-10-15
# - made this some time ago because I'd never heard of the `fileinput` module.
