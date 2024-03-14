import argparse
import turtle

import pygamelib

def apply_rules(symbols):
    new_symbols = ''
    for symbol in symbols:
        if symbol == 'F':
            new_symbols += 'FLFRFRFLF'
        else:
            new_symbols += symbol
    return new_symbols

def generate_l_system(current_symbols, iterations):
    for _ in range(iterations):
        current_symbols = apply_rules(current_symbols)
    return current_symbols

def draw_l_system(symbols, length, angle):
    turtle.speed(0)
    for symbol in symbols:
        if symbol == 'F':
            turtle.forward(length)
        elif symbol == 'L':
            turtle.left(angle)
        elif symbol == 'R':
            turtle.right(angle)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--startx', type=int, default=0)
    parser.add_argument('--starty', type=int, default=0)
    parser.add_argument('--iterations', type=int, default=4)
    parser.add_argument('--length', type=int, default=2)
    parser.add_argument('--angle', type=int, default=90)
    args = parser.parse_args(argv)

    turtle.setup(*args.display_size)
    turtle.bgcolor('black')
    turtle.pencolor('white')

    turtle.penup()
    turtle.setposition(args.startx, args.starty)
    turtle.pendown()

    axiom = 'F'
    l_system = generate_l_system(axiom, args.iterations)
    draw_l_system(l_system, args.length, args.angle)

    turtle.done()

if __name__ == '__main__':
    main()
