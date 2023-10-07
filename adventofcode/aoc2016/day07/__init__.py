import os

class IP(object):

    def __init__(self, ip):
        self.ip = ip

    def _isabba(self, group, n=4):
        i = 0
        while True:
            chars = group[i:i+n]
            if len(chars) < 4:
                return False
            a,b,c,d = chars
            if a != b and a == d and b == c:
                return True
            i += 1
        return False

    def has_abba(self):
        regular, brackets = self.parse()

        for group in brackets:
            if self._isabba(group):
                return False

        for group in regular:
            if self._isabba(group):
                return True

        return False

    def iter_aba(self, group):
        i = 0
        while True:
            chars = group[i:i+3]
            if len(chars) < 3:
                return
            a,b,c = chars
            if a == c and c != b:
                yield chars
            i += 1

    def has_ssl(self):
        regular, brackets = self.parse()

        for group in regular:
            for chars in self.iter_aba(group):
                bab = chars[1] + chars[0] + chars[1]
                for group in brackets:
                    if bab in group:
                        return True

    def parse(self):
        brackets = []
        regular = []
        target = regular

        bucket = ''

        for c in self.ip:
            if c in '[]':
                if bucket:
                    target.append(bucket)
                if c == '[':
                    target = brackets
                else:
                    target = regular
                bucket = ''
                continue
            else:
                bucket += c

        if bucket:
            target.append(bucket)

        return (regular, brackets)


def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).readlines()

def tests():
    assert IP('abba[mnop]qrst').has_abba()
    assert not IP('abcd[bddb]xyyx').has_abba()
    assert not IP('aaaa[qwer]tyui').has_abba()
    assert IP('ioxxoj[asdfgh]zxcvbn').has_abba()

    assert IP('aba[bab]xyz').has_ssl()
    assert not IP('xyx[xyx]xyx').has_ssl()
    assert IP('aaa[kek]eke').has_ssl()
    assert IP('zazbz[bzb]cdb').has_ssl()

def part1():
    tlscount = sum(1 for ipstring in load() if IP(ipstring).has_abba())
    print('Day 7, part 1: %s IPs support TLS' % tlscount)

def part2():
    sslcount = sum(1 for ipstring in load() if IP(ipstring).has_ssl())
    print('Day 7, part 2: %s IPs support SSL' % sslcount)

def main():
    tests()
    part1()
    part2()
