import argparse
import sys
import hashlib
import logging

def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

def interesting(doorid):
    i = 0
    while True:
        h = md5(doorid + str(i))
        if h.startswith('00000'):
            yield h
        i += 1

def findpassword1(doorid):
    log = logging.getLogger('findpassword1')
    password = ''
    for h in interesting(doorid):
        password += h[5]
        log.debug('password: "%s"' % password)
        if len(password) == 8:
            return password

def findpassword2(doorid):
    log = logging.getLogger('findpassword2')
    password = [None] * 8
    for h in interesting(doorid):
        pos, char = int(h[5], 16), h[6]
        try:
            existing = password[pos]
        except IndexError:
            continue
        else:
            if existing is None:
                password[pos] = char
                _ = ''.join(' ' if char is None else char for char in password)
                log.debug('password: "%s"' % (_, ))
                if None not in password:
                    return ''.join(password)

def test1():
    assert findpassword1('abc') == '18f47a30'

def test2():
    assert findpassword2('abc') == '05ace8e3'

def part1():
    print('Day 5, part 1: password is "%s"' % findpassword1('uqwqemis'))

def part2():
    print('Day 5, part 2: password is "%s"' % findpassword2('uqwqemis'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', help='Run test TEST')
    parser.add_argument('--part', help='Run part PART')
    parser.add_argument('--debug', action='store_true', help='Show debugging messages')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(name)s: %(message)s')

    log = logging.getLogger('day05')

    if args.test:
        funcname = 'test' + args.test
    elif args.part:
        funcname = 'part' + args.part
    else:
        parser.exit(message='Must specify option test or part\n')

    selfmod = sys.modules[__name__]
    func = getattr(selfmod, funcname)
    log.debug('running "%s"' % funcname)
    func()
