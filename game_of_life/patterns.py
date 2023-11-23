blinker_string = '\n'.join([
    '   ',
    '###',
    '   ',
])

angel_string = '\n'.join([
    '  #  ',
    '## ##',
    ' # # ',
    '  #  ',
])

# https://www.reddit.com/r/GameOfLifePatterns/comments/rn5949/found_this_cool_pattern_looks_like_a_running/
washing_machine_string = '\n'.join([
    '       #        ',
    '      # #       ',
    '       ##       ',
    '      #  #      ',
    '     # ## #     ',
    '    # #### #    ',
    '   # #    # # # ',
    ' ## ## ## ## # #',
    '# # ## ## ## ## ',
    ' # # #    # #   ',
    '    # #### #    ',
    '     # ## #     ',
    '      #  #      ',
    '       ##       ',
    '       # #      ',
    '        #       ',
])

def string_iter(s):
    for row, line in enumerate(s.splitlines()):
        for col, char in enumerate(line):
            pos = (row, col)
            yield (pos, char)

def pattern_from_string(s):
    for pos, char in string_iter(s):
        if char != ' ':
            yield pos

def blinker():
    return set(pattern_from_string(blinker_string))

def angel():
    return set(pattern_from_string(angel_string))

def washing_machine():
    return set(pattern_from_string(washing_machine_string))
