import argparse
import inspect

import pydatabase as db

class Human(db.Table):
    __tablename__ = 'humans'
    name = db.Column()


class Parent(db.Table):
    __tablename__ = 'parents'
    parent = db.Column()
    child = db.Column()


class Relation(db.Table):
    __tablename__ = 'relations'


def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    john = Human(name='john')
    jane = Human(name='jane')
    paul = Human(name='paul')

    print(Human.__instances__)

if __name__ == '__main__':
    main()
