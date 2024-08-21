def python_add(a, b):
    return a + b

def bitwise_add(a, b):
    while b != 0:
        carry = a & b  # calculate carry
        a = a ^ b      # sum without carry
        b = carry << 1 # carry shifted left
    return a
