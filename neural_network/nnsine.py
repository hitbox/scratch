import math
import random
import unittest

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)

def initialize_weights(input_size, hidden_size, output_size):
    weights_input_hidden = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
    weights_hidden_output = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]
    bias_hidden = [random.uniform(-1, 1) for _ in range(hidden_size)]
    bias_output = [random.uniform(-1, 1) for _ in range(output_size)]
    return weights_input_hidden, weights_hidden_output, bias_hidden, bias_output

def forward_propagation(inputs, weights_input_hidden, weights_hidden_output, bias_hidden, bias_output):
    hidden_layer_input = [sum(inputs[i] * weights_input_hidden[i][j] for i in range(len(inputs))) for j in range(len(weights_input_hidden[0]))]
    hidden_layer_output = [sigmoid(x + b) for x, b in zip(hidden_layer_input, bias_hidden)]

    output_layer_input = [sum(hidden_layer_output[i] * weights_hidden_output[i][j] for i in range(len(hidden_layer_output))) for j in range(len(weights_hidden_output[0]))]
    output = [sigmoid(x + b) for x, b in zip(output_layer_input, bias_output)]

    return hidden_layer_output, output

def backpropagation(inputs, labels, hidden_layer_output, output, weights_input_hidden, weights_hidden_output, bias_hidden, bias_output):
    error = [a - b for a, b in zip(labels, output)]
    d_output = [e * sigmoid_derivative(o) for e, o in zip(error, output)]

    error_hidden = [sum(d_output[j] * weights_hidden_output[i][j] for j in range(len(d_output))) for i in range(len(hidden_layer_output))]
    d_hidden = [e * sigmoid_derivative(o) for e, o in zip(error_hidden, hidden_layer_output)]

    # Update weights and biases
    for i in range(len(weights_hidden_output)):
        for j in range(len(weights_hidden_output[0])):
            weights_hidden_output[i][j] += hidden_layer_output[i] * d_output[j]

    for i in range(len(weights_input_hidden)):
        for j in range(len(weights_input_hidden[0])):
            weights_input_hidden[i][j] += inputs[i] * d_hidden[j]

    bias_output = [b + d for b, d in zip(bias_output, d_output)]
    bias_hidden = [b + d for b, d in zip(bias_hidden, d_hidden)]

    return weights_input_hidden, weights_hidden_output, bias_hidden, bias_output, error

def train_neural_network(epochs):
    # One input value for sine function
    input_size = 1
    # Arbitrary hidden layer size
    hidden_size = 8
    # One output value (sine value)
    output_size = 1

    # Creating a dataset for sine function
    # Input values from -10 to 10
    inputs = [[i / 10] for i in range(-100, 100)]
    # Corresponding sine values
    labels = [[math.sin(i[0])] for i in inputs]

    # Initialize weights and biases
    weights_input_hidden, weights_hidden_output, bias_hidden, bias_output = initialize_weights(input_size, hidden_size, output_size)

    for epoch in range(epochs):
        total_error = 0
        for i in range(len(inputs)):
            hidden_layer_output, output = forward_propagation(inputs[i], weights_input_hidden, weights_hidden_output, bias_hidden, bias_output)

            weights_input_hidden, weights_hidden_output, bias_hidden, bias_output, error = backpropagation(
                inputs[i], labels[i], hidden_layer_output, output, weights_input_hidden, weights_hidden_output, bias_hidden, bias_output)

            # Accumulating absolute error
            total_error += abs(error[0])

        if epoch % 100 == 0:
            print(f'Epoch {epoch} - Total Error: {total_error}')

    return weights_input_hidden, weights_hidden_output, bias_hidden, bias_output

# Making predictions for sine function
def predict(inputs, weights_input_hidden, weights_hidden_output, bias_hidden, bias_output):
    _, output = forward_propagation(inputs, weights_input_hidden, weights_hidden_output, bias_hidden, bias_output)
    return output

# Training the neural network
trained_weights = train_neural_network(epochs=1000)

# Predicting sine values using the trained network
# Example input value for prediction
input_value = [0.5]
predicted_output = predict(input_value, *trained_weights)
print(f"Sine value for input {input_value[0]}: {predicted_output[0]}")
