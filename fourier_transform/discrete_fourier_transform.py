import argparse
import math

def discrete_fourier_transform(x):
    N = len(x)
    X = []
    for k in range(N):
        X_k = 0
        for n in range(N):
            angle = math.tau * k * n / N
            X_k += x[n] * (math.cos(angle) - 1j * math.sin(angle))
        X.append(X_k)
    return X

def chatgpt2():
    num_samples = len(signal)
    dft_result = []

    for k in range(num_samples):
        X_k = 0
        for n in range(num_samples):
            angle = -math.tau * k * n / num_samples
            complex_exponential = complex(math.cos(angle), math.sin(angle))
            X_k += signal[n] * complex_exponential
        dft_result.append(X_k)
    return dft_result

def discrete_fourier_transform(signal):
    """
    Compute the Discrete Fourier Transform (DFT) of a given signal.
    """
    num_samples = len(signal)
    container = type(signal)
    dft_result = container(
        sum(
            signal_n * complex(
                math.cos(-math.tau * k * n / num_samples),
                math.sin(-math.tau * k * n / num_samples),
            )
            for n, signal_n in enumerate(signal)
        )
        for k in range(num_samples)
    )
    return dft_result

def inverse_dft(X):
    N = len(X)
    x = []
    for n in range(N):
        x_n = 0
        for k in range(N):
            angle = math.tau * k * n / N
            x_n += X[k] * (math.cos(angle) + 1j * math.sin(angle))
        x.append(x_n / N)
    return x

def example2():
    # this example after asking chatgpt for my preferences
    # Sample input signal (a list of complex numbers)
    signal = [1, 2, 3, 4]

    # Compute the DFT of the input signal
    dft_result = discrete_fourier_transform(signal)

    # Print the DFT results for each frequency component
    for frequency, X_k in enumerate(dft_result):
        print(f'DFT({frequency}) = {X_k.real} + {X_k.imag}j')

def example():
    # Example usage:
    input_signal = list(range(5))
    X = discrete_fourier_transform(input_signal)
    reconstructed_signal = inverse_dft(X)
    print('Input Signal:', input_signal)
    print('DFT:', X)
    print('Inverse DFT:', [round(x.real, 2) for x in reconstructed_signal])

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    args = parser.parse_args(argv)

    if args.input:
        with open(args.input) as input_file:
            signal = list(map(float, input_file.readlines()))
            dft = discrete_fourier_transform(signal)
            for frequency, X_k in enumerate(dft):
                print(f'DFT({frequency}) = {X_k}')
    else:
        example2()

if __name__ == '__main__':
    main()

# https://chat.openai.com/c/3040c27e-87cb-4bfd-84f4-2b2448e76a02
# https://chat.openai.com/c/6045183d-a2a1-442d-9777-747a71c3292b
