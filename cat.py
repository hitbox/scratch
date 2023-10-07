import fileinput

def main():
    for line in fileinput.input():
        print(line, end='')

if __name__ == '__main__':
    main()
