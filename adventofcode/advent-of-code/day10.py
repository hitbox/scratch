#!python
def look_and_say(s):
    """
    Way faster than look_and_say1
    """
    rv = ''
    i = 0
    l = len(s)
    while i < l:
        n = 1
        c = s[i]
        i += 1
        while i < l and s[i] == c:
            i += 1
            n += 1
        rv += str(n) + c
    return rv

def look_and_say1(s):
    rv = ''

    def getrun(ofchar, s):
        numc = 0
        for c in s:
            if c != ofchar:
                break
            numc += 1
        return numc

    i = 0
    while True:
        try:
            ofchar = s[i]
        except IndexError:
            break

        numc = getrun(ofchar, s[i:])
        rv += '%s%s' % (numc, ofchar)
        i += numc

    return rv

def test():
    assert look_and_say('1') == '11'
    assert look_and_say('11') == '21'
    assert look_and_say('21') == '1211'
    assert look_and_say('1211') == '111221'
    assert look_and_say('111221') == '312211'

def run(inputstr, n):
    for _ in range(n):
        rv = look_and_say(inputstr)
        inputstr = rv
    return rv

def main():
    inputstr = '1321131112'
    print 'Part 1: length %s' % len(run(inputstr, 40))
    print 'Part 2: length %s' % len(run(inputstr, 50))

if __name__ == '__main__':
    test()
    main()
