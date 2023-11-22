import argparse
import math
import random

from pprint import pprint

def heaviside(value):
    # or unit step function
    # https://en.wikipedia.org/wiki/Heaviside_step_function
    if value > 0:
        return 1
    else:
        return 0

def sigmoid(value):
    return 1 / (1 + math.exp(-value))

def run(x, y, training_iterations=None, activation_function=None):
    if training_iterations is None:
        training_iterations = 1000

    if activation_function is None:
        activation_function = heaviside
    elif isinstance(activation_function, str):
        activation_function = eval(activation_function)

    learning_rate = 1
    bias = 1
    # two neurons and the bias (three)
    weights = [random.random() for _ in range(3)]

    def perceptron(input1, input2, output):
        inputs = [input1, input2, bias]
        items = zip(inputs, weights)
        value = activation_function(sum(v * w for v, w in items))
        error = output - value
        for (index, weight), input_ in zip(enumerate(weights), inputs):
            weights[index] += error * input_ * learning_rate

    for _ in range(training_iterations):
        perceptron(1,1,1)
        perceptron(1,0,1)
        perceptron(0,1,1)
        perceptron(0,0,0)

    items = zip([x, y, bias], weights)
    output = activation_function(sum(v * w for v, w in items))
    return output

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=int)
    parser.add_argument('y', type=int)
    parser.add_argument('--training-iterations')
    parser.add_argument('--activation-function')
    args = parser.parse_args(argv)
    output = run(args.x, args.y, args.training_iterations, args.activation_function)
    print(f'{args.x} or {args.y} is {output}')

if __name__ == '__main__':
    main()

# 2023-11-22
# - https://towardsdatascience.com/first-neural-network-for-beginners-explained-with-code-4cfd37e06eaf
