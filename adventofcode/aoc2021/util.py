from pathlib import Path

def input_filename(day_number):
    path = Path('inputs') / f'day{day_number:02d}.input.txt'
    return path

def iter_table_indexes(table):
    for rowi, row in enumerate(table):
        for coli, cell in enumerate(row):
            yield (rowi, coli)

def readinput(day_number):
    with open(input_filename(day_number)) as fp:
        return fp.read()
