import math
import random

def rot(n, x, y, rx, ry):
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        # Swap x and y
        x, y = y, x
    return x, y

def d2xy(n, d):
    x = y = 0
    s = 1
    t = d
    while s < n:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        x, y = rot(s, x, y, rx, ry)
        x += s * rx
        y += s * ry
        t = t // 4
        s *= 2
    return x, y

def character_brightness(val):
    # Use character brightness levels
    if val < 0.2:
        char = '.'
    elif val < 0.4:
        char = '-'
    elif val < 0.6:
        char = '*'
    elif val < 0.8:
        char = 'O'
    else:
        char = '#'
    return char

# Simulate 1D data with periodic structure and noise
size = 256  # Must be a power of 4 (for Hilbert)

def func(i):
    return math.sin(i * math.tau / 32) + random.uniform(-0.3, 0.3)

data = [func(i) for i in range(size)]

order = 8  # 2^8 = 256 points
n = 2 ** (order // 2)
grid = [[' ' for _ in range(n)] for _ in range(n)]

# Normalize data to 0-1
min_val = min(data)
max_val = max(data)
norm = [(v - min_val) / (max_val - min_val) for v in data]

for i, val in enumerate(norm):
    x, y = d2xy(n, i)
    grid[y][x] = character_brightness(val)

# Print result
for row in grid:
    print(''.join(row))

print(''.join(character_brightness(val) for val in norm))
