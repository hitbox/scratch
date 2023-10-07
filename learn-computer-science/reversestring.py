# randomly found this
# https://nsurendar.blogspot.com/2010/01/reverse-string-using-xor-and-without.html

def reversestring(s):
    s = list(map(ord, s))

    end = len(s) - 1
    start = 0

    while start < end:
        s[start] ^= s[end]
        s[end] ^= s[start]
        s[start] ^= s[end]

        start += 1
        end -= 1

    return ''.join(map(chr, s))

assert reversestring('abcdefg') == 'gfedcba'
