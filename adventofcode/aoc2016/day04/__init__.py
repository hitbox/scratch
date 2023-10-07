import os
import re

alphabet = 'abcdefghijklmnopqrstuvwxyz'

class Room(object):

    _room_re = re.compile('^(.*)-(\d+)\[([a-z]+)\]$')

    def __init__(self, name):
        self.name = name

    def parse_room(self):
        m = self._room_re.match(self.name)
        if m:
            encrypted, sectorid, checksum = m.groups()
            return (encrypted, int(sectorid), checksum)

    def mostcommon(self):
        rv = self.parse_room()
        if not rv:
            return
        encrypted_name, _, _ = rv
        s = ''.join(encrypted_name.split('-'))
        d = {}
        for c in s:
            if c not in d:
                d[c] = 0
            d[c] += 1
        charcounts = ((c, d[c]) for c in set(s) )
        return sorted(sorted(charcounts, key=lambda t: t[0]), key=lambda t: t[1], reverse=True)

    def encryptedchecksum(self):
        "The checksum of the 5 most common characters"
        rv = ''.join(c for i,c in enumerate(char for char,count in self.mostcommon()) if i < 5)
        return rv

    def is_real(self):
        rv = self.parse_room()
        if rv:
            _, _, checksum = rv
            return self.encryptedchecksum() == checksum
        return False

    def sectorid(self):
        rv = self.parse_room()
        if rv:
            return rv[1]

    def shiftedindex(self, char, amount):
        return (alphabet.index(char) + amount) % len(alphabet)

    def unencrypt(self):
        rv = self.parse_room()
        if rv:
            name, sector, _ = rv
            return ''.join(' ' if char == '-' else alphabet[self.shiftedindex(char, sector)] for char in name)


def tests():
    sector_total = 0

    room = Room('aaaaa-bbb-z-y-x-123[abxyz]')
    assert room.is_real()
    sector_total += room.sectorid()

    room = Room('a-b-c-d-e-f-g-h-987[abcde]')
    assert room.is_real()
    sector_total += room.sectorid()

    room = Room('not-a-real-room-404[oarel]')
    assert room.is_real()
    sector_total += room.sectorid()

    room = Room('totally-real-room-200[decoy]')
    assert not room.is_real()

    assert sector_total == 1514

def load():
    return open(os.path.join(os.path.dirname(__file__), 'input.txt')).readlines()

def tests2():
    assert Room('qzmt-zixmtkozy-ivhz-343[zimto]').unencrypt() == 'very encrypted name'

def part1():
    total = 0
    for line in load():
        room = Room(line)
        if room.is_real():
            total += room.sectorid()

    print('Day 4, part 1: total sector id is %s' % total)

def part2():
    for line in load():
        room = Room(line)
        if not room.is_real():
            continue
        if 'northpole' in room.unencrypt().lower():
            print('Sector ID of %s is %s' % (room.unencrypt(), room.sectorid()))

def main():
    tests()
    part1()
    tests2()
    part2()
