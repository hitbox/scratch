import argparse
import math
import operator
import random

def training_binary(func, *biases):
    for x in range(2):
        for y in range(2):
            yield (func(x, y), x, y) + biases

def training_or():
    yield from training_binary(operator.or_)

def training_xor():
    yield from training_binary(operator.xor)

def heaviside(value):
    # or unit step function
    # https://en.wikipedia.org/wiki/Heaviside_step_function
    if value > 0:
        return 1
    else:
        return 0

def sigmoid(value):
    return 1 / (1 + math.exp(-value))

def train(weights, training, activation_function, iterations=None):

    if iterations is None:
        iterations = 1_000

    for _ in range(iterations):
        for expect, *inputs in training():
            value = activation_function(sum(v * w for v, w in zip(inputs, weights, strict=True)))
            error = expect - value
            weights = [
                weight + error * input_
                for weight, input_ in zip(weights, inputs, strict=True)
            ]

    return weights

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=int)
    parser.add_argument('y', type=int)
    parser.add_argument('--training-iterations', type=int)
    parser.add_argument('--activation-function')
    args = parser.parse_args(argv)

    activation_function = args.activation_function
    if activation_function is None:
        activation_function = heaviside
    elif isinstance(activation_function, str):
        activation_function = eval(activation_function)

    weights = [random.random() if i < 2 else 1 for i in range(3)]
    func = operator.xor
    training = lambda: training_binary(func, 1)
    weights = train(weights, training, activation_function)

    output = activation_function(
        sum(v * w for v, w in zip([args.x, args.y, 1], weights, strict=True))
    )
    print(f'{args.x} {func.__name__} {args.y} is {output:.8f}')

if __name__ == '__main__':
    main()

# 2023-11-22
# - https://towardsdatascience.com/first-neural-network-for-beginners-explained-with-code-4cfd37e06eaf
