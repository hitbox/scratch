import argparse
import turtle

def apply_rules(symbols):
    new_symbols = ""
    for symbol in symbols:
        if symbol == "F":
            new_symbols += "F+F-F-F+F"
        else:
            new_symbols += symbol
    return new_symbols

def generate_l_system(axiom, iterations):
    current_symbols = axiom
    for _ in range(iterations):
        current_symbols = apply_rules(current_symbols)
    return current_symbols

def draw_l_system(symbols, length, angle):
    turtle.speed(0)
    for symbol in symbols:
        if symbol == "F":
            turtle.forward(length)
        elif symbol == "+":
            turtle.left(angle)
        elif symbol == "-":
            turtle.right(angle)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--iterations', type=int, default=4)
    args = parser.parse_args(argv)
    axiom = "F"
    l_system = generate_l_system(axiom, args.iterations)

    length = 2
    angle = 90
    draw_l_system(l_system, length, angle)

    turtle.done()

if __name__ == "__main__":
    main()
