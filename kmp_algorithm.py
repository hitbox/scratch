def compute_prefix_function(pattern):
    m = len(pattern)
    pi = [0] * m
    k = 0
    for q in range(1, m):
        while k > 0 and pattern[k] != pattern[q]:
            k = pi[k - 1]
        if pattern[k] == pattern[q]:
            k += 1
        pi[q] = k
    return pi

def kmp_search(text, pattern):
    n = len(text)
    m = len(pattern)
    pi = compute_prefix_function(pattern)
    q = 0
    indices = []
    for i in range(n):
        while q > 0 and pattern[q] != text[i]:
            q = pi[q - 1]
        if pattern[q] == text[i]:
            q += 1
        if q == m:
            indices.append(i - m + 1)
            q = pi[q - 1]
    return indices

def example():
    # Example usage:
    text = "ABABDABACDABABCABAB"
    pattern = "ABABCABAB"
    print("Pattern found at indices:", kmp_search(text, pattern))

# 2024-04-15 Mon.
# https://www.cambridge.org/core/journals/journal-of-functional-programming/article/knuthmorrispratt-illustrated/8EFA77D663D585B68630E372BCE1EBA4#
# https://chat.openai.com/c/f16cae1f-dd64-456a-bf57-4d1e3272d491
# - Jotting this down to look at later.
