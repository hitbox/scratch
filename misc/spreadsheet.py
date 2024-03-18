# 2023-06-11
# https://code.activestate.com/recipes/355045-spreadsheet/?in=lang-python
# Seen this before, capturing it now.

import math

class SpreadSheet:

    def __init__(self, tools=None):
        self.cells = {}
        if tools is None:
            tools = {}
        self.tools = tools

    def __setitem__(self, key, formula):
        self.cells[key] = formula

    def __getitem__(self, key):
        return eval(self.cells[key], self.tools, self)

    def get_formula(self, key):
        return self.cells[key]


ss = SpreadSheet(tools=vars(math))

ss['a1'] = '5'
ss['a2'] = 'a1 * 6'
ss['a3'] = 'a2 * 7'
assert ss['a3'] == 210

ss['b1'] = 'sin(pi/4)'
assert ss['b1'] == math.sin(math.pi / 4)

assert ss.get_formula('b1') == 'sin(pi/4)'
