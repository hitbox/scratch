import argparse

import numpy as np

class CharRNN:

    def __init__(self, hidden_size, seq_length, learning_rate):
        self.hidden_size = hidden_size
        self.seq_length = seq_length
        self.learning_rate = learning_rate

        self.chars = list('abcdefghijklmnopqrstuvwxyz ')
        self.char_to_idx = {ch: i for i, ch in enumerate(self.chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(self.chars)}
        self.vocab_size = len(self.chars)

        self.Wxh = np.random.randn(hidden_size, self.vocab_size) * 0.01
        self.Whh = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Why = np.random.randn(self.vocab_size, hidden_size) * 0.01
        self.bh = np.zeros((hidden_size, 1))
        self.by = np.zeros((self.vocab_size, 1))

        self.h_prev = np.zeros((hidden_size, 1))

    def forward(self, inputs):
        xs, hs, ys, ps = {}, {}, {}, {}
        hs[-1] = np.copy(self.h_prev)

        for t in range(len(inputs)):
            xs[t] = np.zeros((self.vocab_size, 1))
            xs[t][self.char_to_idx[inputs[t]]] = 1
            hs[t] = np.tanh(np.dot(self.Wxh, xs[t]) + np.dot(self.Whh, hs[t - 1]) + self.bh)
            ys[t] = np.dot(self.Why, hs[t]) + self.by
            ps[t] = np.exp(ys[t]) / np.sum(np.exp(ys[t]))

        return xs, hs, ys, ps

    def backward(self, inputs, targets, xs, hs, ps):
        dWxh, dWhh, dWhy = np.zeros_like(self.Wxh), np.zeros_like(self.Whh), np.zeros_like(self.Why)
        dbh, dby = np.zeros_like(self.bh), np.zeros_like(self.by)
        dh_next = np.zeros_like(hs[0])

        for t in reversed(range(len(inputs))):
            dy = np.copy(ps[t])
            dy[self.char_to_idx[targets[t]]] -= 1
            dWhy += np.dot(dy, hs[t].T)
            dby += dy
            dh = np.dot(self.Why.T, dy) + dh_next
            dhraw = (1 - hs[t] * hs[t]) * dh
            dbh += dhraw
            dWxh += np.dot(dhraw, xs[t].T)
            dWhh += np.dot(dhraw, hs[t - 1].T)
            dh_next = np.dot(self.Whh.T, dhraw)

        for dparam in [dWxh, dWhh, dWhy, dbh, dby]:
            np.clip(dparam, -5, 5, out=dparam)

        self.Wxh -= self.learning_rate * dWxh
        self.Whh -= self.learning_rate * dWhh
        self.Why -= self.learning_rate * dWhy
        self.bh -= self.learning_rate * dbh
        self.by -= self.learning_rate * dby

        self.h_prev = hs[len(inputs) - 1]

    def train(self, data, epochs):
        for epoch in range(epochs):
            ptr = 0
            for _ in range(len(data) // self.seq_length):
                inputs = [ch for ch in data[ptr:ptr+self.seq_length]]
                targets = [ch for ch in data[ptr+1:ptr+self.seq_length+1]]

                if len(inputs) == self.seq_length:
                    xs, hs, ys, ps = self.forward(inputs)
                    self.backward(inputs, targets, xs, hs, ps)

                ptr += self.seq_length

            if epoch % 100 == 0:
                print(f'Epoch: {epoch}/{epochs}')

    def sample(self, seed, n):
        idx = self.char_to_idx[seed]
        x = np.zeros((self.vocab_size, 1))
        x[idx] = 1
        h = np.copy(self.h_prev)
        generated_text = seed

        for _ in range(n):
            h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, h) + self.bh)
            y = np.dot(self.Why, h) + self.by
            p = np.exp(y) / np.sum(np.exp(y))

            idx = np.random.choice(range(self.vocab_size), p=p.ravel())
            x = np.zeros((self.vocab_size, 1))
            x[idx] = 1
            generated_text += self.idx_to_char[idx]

        return generated_text

def run():
    data = "hello world how are you doing today"
    rnn = CharRNN(hidden_size=100, seq_length=25, learning_rate=0.1)
    rnn.train(data, epochs=1000)

    generated_text = rnn.sample(seed='h', n=50)
    print("Generated Text:")
    print(generated_text)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == "__main__":
    main()

# https://chat.openai.com/c/dbeb3038-c6f0-4df5-ab49-d8b1d5a9c7a5
