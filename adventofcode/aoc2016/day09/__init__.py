import os

def _decompress(s, recurse=False):
    stream = iter(s)
    for c in stream:
        if c != '(':
            yield c
            continue

        length = ''
        while True:
            c = next(stream)
            if not c.isnumeric():
                break
            length += c
        length = int(length)

        times = ''
        while True:
            c = next(stream)
            if not c.isnumeric():
                break
            times += c
        times = int(times)

        repeat = ''.join(next(stream) for _ in range(length))

        if recurse:
            repeat = decompress(repeat, recurse=True)

        for _ in range(times):
            yield repeat

def decompress(s, recurse=False):
    return ''.join(_decompress(s, recurse=recurse))

def tests():
    assert decompress('ADVENT') == 'ADVENT'
    assert decompress('A(1x5)BC') == 'ABBBBBC'
    assert decompress('(3x3)XYZ') == 'XYZXYZXYZ'
    assert decompress('A(2x2)BCD(2x2)EFG') == 'ABCBCDEFEFG'
    assert decompress('(6x1)(1x3)A') == '(1x3)A'
    assert decompress('X(8x2)(3x3)ABCY') == 'X(3x3)ABC(3x3)ABCY'

    assert decompress('(3x3)XYZ', recurse=True) == 'XYZXYZXYZ'
    assert decompress('X(8x2)(3x3)ABCY', recurse=True) == 'XABCABCABCABCABCABCY'

    rv = decompress('(27x12)(20x12)(13x14)(7x10)(1x12)A', recurse=True)
    assert all(c == 'A' for c in rv)
    assert len(rv) == 241920

    assert 445 == len(decompress('(25x3)(3x3)ABC(2x3)XY(5x2)PQRSTX(18x9)(3x2)TWO(5x7)SEVEN', recurse=True))

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).read().strip()

def main():
    tests()
    s = decompress(load())
    # NOTE: One stickin whitespace character got me! Probably the newline.
    print('Day 9, part 1: Decompressed length %s' % len(s))

    count = sum(len(c) for c in _decompress(load(), recurse=True) if c.strip())
    print('Day 9, part 2: Recursive decompressed length %s' % count)
