import argparse
import itertools as it
import sqlite3

def in_positional_placeholders(iterable):
    return ', '.join('?' for _ in iterable)

def in_named_placeholders(iterable, prefix):
    return ', '.join(f':{prefix}{i}' for i, _ in enumerate(iterable))

def main(argv=None):
    # investigating query parameters, named and otherwise
    # specifically passing a tuple into the `IN` operator
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute("CREATE TABLE movies(title, year, score)")
    values = ((f'movie{i}', 1900 + i, i) for i in range(100))
    cur.executemany(
        "INSERT INTO movies (title, year, score) VALUES (?, ?, ?)",
        values
    )
    conn.commit()

    scores = {f'score{i}': value for i, value in enumerate((35,))}
    score_in_placeholders = in_named_placeholders(scores, 'score')
    sql = (
        f"SELECT * FROM movies"
        f" WHERE score IN ({score_in_placeholders})"
        f" AND year > :year"
    )
    print(sql)
    params = dict(year=50)
    params.update(scores)
    print(params)
    result = cur.execute(sql, params)
    for row in result:
        print(row)

if __name__ == '__main__':
    main()
