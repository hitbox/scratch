import argparse
import contextlib
import operator
import os
import unittest

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class TestEvaluate(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(evaluate('', 1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('X', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('Y', 1, 2, 3), (0, 0, 2))
        self.assertEqual(evaluate('T', 1, 2, 3), (0, 0, 3))
        self.assertEqual(evaluate('XY', 1, 2, 3), (0, 1, 2))
        self.assertEqual(evaluate('XYT', 1, 2, 3), (1, 2, 3))
        self.assertEqual(evaluate('XYTXYTXY', 1, 2, 3), (3, 1, 2))

    def test_digits(self):
        self.assertEqual(evaluate('N1', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('N2', 1, 2, 3), (0, 0, 2))
        self.assertEqual(evaluate('N3', 1, 2, 3), (0, 0, 3))
        self.assertEqual(evaluate('N4', 1, 2, 3), (0, 0, 4))
        self.assertEqual(evaluate('N5', 1, 2, 3), (0, 0, 5))
        self.assertEqual(evaluate('N6', 1, 2, 3), (0, 0, 6))
        self.assertEqual(evaluate('N7', 1, 2, 3), (0, 0, 7))
        self.assertEqual(evaluate('N8', 1, 2, 3), (0, 0, 8))
        self.assertEqual(evaluate('N9', 1, 2, 3), (0, 0, 9))
        self.assertEqual(evaluate('N8N9', 1, 2, 3), (0, 8, 9))
        self.assertEqual(evaluate('N7N8N9', 1, 2, 3), (7, 8, 9))
        self.assertEqual(evaluate('N0N1N2N3N4N5N6N7', 1, 2, 3), (5, 6, 7))
        self.assertEqual(evaluate('N4N4N4N4***N1-', 1, 2, 3), (0, 0, 255))

    def test_other(self):
        self.assertEqual(evaluate('XYD', 1, 2, 3), (1, 2, 2))
        self.assertEqual(evaluate('N4N5N6D', 1, 2, 3), (5, 6, 6))
        self.assertEqual(evaluate('XYP', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('XYS', 1, 2, 3), (0, 2, 1))
        self.assertEqual(evaluate('XYTS', 1, 2, 3), (1, 3, 2))
        self.assertEqual(evaluate('XYTR', 1, 2, 3), (2, 3, 1))
        self.assertEqual(evaluate('N9XYTR', 1, 2, 3), (2, 3, 1))
        self.assertEqual(evaluate('N9XYTRP', 1, 2, 3), (9, 2, 3))

    def test_binary_operations(self):
        self.assertEqual(evaluate('XY+', 1, 2, 3), (0, 0, 3))
        self.assertEqual(evaluate('N1N1+', 1, 2, 3), (0, 0, 2))
        self.assertEqual(evaluate('XYT++', 1, 2, 3), (0, 0, 6))
        #self.assertEqual(evaluate('XY+', MAX_VAL - 10, 10, 3), (0, 0, MAX_VAL))
        self.assertEqual(evaluate('XY-', 1, 2, 3), (0, 0, -1))
        self.assertEqual(evaluate('XY*', 3, 2, 1), (0, 0, 6))
        self.assertEqual(evaluate('XY*', -3, 2, 1), (0, 0, -6))
        self.assertEqual(evaluate('XY*', 3, -2, 1), (0, 0, -6))
        self.assertEqual(evaluate('XY*', -3, -2, 1), (0, 0, 6))
        self.assertEqual(evaluate('XY/', 4, 2, 1), (0, 0, 2))
        self.assertEqual(evaluate('XY/', 4, 3, 1), (0, 0, 1))
        self.assertEqual(evaluate('XY/', -4, 3, 1), (0, 0, -1))
        self.assertEqual(evaluate('XY/', 4, -3, 1), (0, 0, -1))
        self.assertEqual(evaluate('XY/', 4, 5, 1), (0, 0, 0))
        self.assertEqual(evaluate('XY%', 4, 5, 1), (0, 0, 4))
        self.assertEqual(evaluate('XY%', 7, 5, 1), (0, 0, 2))
        self.assertEqual(evaluate('XY%', 7, -5, 1), (0, 0, 2))
        self.assertEqual(evaluate('XY%', -7, 5, 1), (0, 0, 3))
        self.assertEqual(evaluate('XY%', -7, -5, 1), (0, 0, 3))
        self.assertEqual(evaluate('XY^', 1, 3, 2), (0, 0, 2))
        self.assertEqual(evaluate('XY&', 1, 3, 2), (0, 0, 1))
        self.assertEqual(evaluate('XY|', 1, 3, 2), (0, 0, 3))
        self.assertEqual(evaluate('X!', 0, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('X!', 1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('Y!', 1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('T!', 1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('X!', -1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('X!', -2, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('X!!', 2, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('XY=', 1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('XX=', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('XY<', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('XY>', 1, 2, 3), (0, 0, 0))

    def test_loop(self):
        self.assertEqual(evaluate('XN0[N1+]', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('XN0N1-[N1+]', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('XN1[N1+]', 1, 2, 3), (0, 0, 2))
        self.assertEqual(evaluate('N2N3[N4+]', 1, 2, 3), (0, 0, 14))
        self.assertEqual(evaluate('XTX-[N9+]', 1, 2, 3), (0, 0, 19))
        self.assertEqual(evaluate('XTX-[N9+]X', 1, 2, 3), (0, 19, 1))
        self.assertEqual(evaluate('XX-[N4+]', 1, 2, 3), (0, 0, 0))
        self.assertEqual(evaluate('XX-[N4+]X', 1, 2, 3), (0, 0, 1))
        self.assertEqual(evaluate('N0N2[N3[N1+]]', 1, 2, 3), (0, 0, 6))
        self.assertEqual(evaluate('N0N2[N3[N4[N1+]]]', 1, 2, 3), (0, 0, 24))

    # TODO
    # - implement their errors?
    # - error tests

    @unittest.expectedFailure
    def test_final(self):
        # - why extra argument?
        self.assertEqual(evaluate('XYT', 1, 2, 3, 3), (1, 2, 3))


def eval_binary(op, a, b):
    if op == '+':
        c = a + b
    elif op == '-':
        c = a - b
    elif op == '*':
        c = a * b
    elif op == '^':
        c = a ^ b
    elif op == '&':
        c = a & b
    elif op == '|':
        c = a | b
    elif op == '=':
        c = a == b
    elif op == '<':
        c = a < b
    elif op == '>':
        c = a > b
    elif op == '/':
        c = int(a / b)
    elif op == '%':
        c = a % b
        if c < 0:
            c += abs(b)
    return c

def evaluate(code, x, y, t):
    data_stack = []
    loop_stack = []

    n = 0 # push X, Y, T, N

    index = 0
    while index < len(code):
        op = code[index]
        if op in 'XYTN':
            # push X, Y, T, N
            data_stack.append(locals()[op.lower()])
            index += 1
        elif op.isdigit():
            # add decimal digit
            a = data_stack[-1]
            b = int(op)
            c = 10 * a + b
            data_stack[-1] = c
            index += 1
        elif op == 'C':
            # clip value
            a = data_stack[-1]
            if a > 255:
                a = 255
            elif a < 0:
                a = 0
            data_stack.append(a)
            index += 1
        elif op == 'D':
            # duplicate
            data_stack.append(data_stack[-1])
            index += 1
        elif op == 'P':
            # pop
            data_stack.pop()
            index += 1
        elif op == 'S':
            # swap
            data_stack[-2:] = data_stack[-2:][::-1]
            index += 1
        elif op == 'R':
            # rotate
            a, b, c = data_stack[-3:]
            data_stack[-3:] = b, c, a
            index += 1
        elif op == '!':
            data_stack[-1] = not data_stack[-1]
            index += 1
        elif op in '+-*^&|=<>/%':
            # binary operations
            b = data_stack.pop()
            a = data_stack.pop()
            c = eval_binary(op, a, b)
            data_stack.append(c)
            index += 1
        elif op == '[':
            # begin loop
            a = data_stack.pop()
            if a > 0:
                # enter loop
                loop_stack.append((index + 1, a))
                index += 1
            else:
                # skip loop
                depth = 1
                index += 1
                while depth != 0 and index < len(code):
                    ch = code[index]
                    if ch == '[':
                        depth += 1
                    elif ch == ']':
                        depth -= 1
                    index += 1
        elif op == ']':
            # close loop
            jump_index, a = loop_stack.pop()
            a -= 1
            if a > 0:
                loop_stack.append((jump_index, a))
                index = jump_index
            else:
                index += 1
        elif op == 'W':
            # write stack and halt
            raise NotImplementedError
        elif op == 'F':
            # set frame interval
            raise NotImplementedError
        elif op == 'M':
            # set mode
            raise NotImplementedError
        else:
            raise ValueError(f'unknown operator {op!r}')

    # pop-push color components
    result = data_stack[-3:]
    while len(result) < 3:
        result.insert(0, 0)

    return tuple(result)

GRID_SIZE = 256
SCALE = 4

def animate_code(code):
    screen = pygame.display.set_mode((GRID_SIZE * SCALE,)*2)
    world = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 120

    t = 0
    running = True
    while running:
        #elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                color = evaluate(code, x, y, t)
                pygame.draw.rect(screen, color, (x * SCALE, y * SCALE, SCALE, SCALE))

        pygame.display.flip()
        t += 1

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('code')
    args = parser.parse_args(argv)
    animate_code(args.code)

if __name__ == '__main__':
    main()

# https://github.com/susam/fxyt
