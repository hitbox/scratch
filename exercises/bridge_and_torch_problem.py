"""
Python program to find minimum time required to send people on other side of bridge
"""

from operator import itemgetter

dp = [[0 for _ in range(2)] for _ in range(1 << 20)]

def old_find_min_value_person_index():
    # (1)
    min_row = float('inf')
    person = 0
    for i in range(n):
        # Select one people whose time is less among all others present at
        # right side
        if (rightmask & (1 << i)) != 0:
            if min_row > arr[i]:
                person = i
                min_row = arr[i]


def find_min_time(leftmask, turn, arr, n):
    """
    Utility function to find total time required to send people to other side
    of bridge
    """
    # If all people has been transferred
    if leftmask == 0:
        return 0

    res = dp[leftmask][turn]

    # If we already have solved this subproblem, return the answer.
    if ~res != 0:
        return res

    # Calculate mask of right side of people
    rightmask = ((1 << n) - 1) ^ leftmask

    # if turn == 1 means currently people are at right side, thus we need to
    # transfer people to the left side
    if turn:
        # (1)
        right_indices = (i for i in range(n) if (1 << i) & rightmask)
        person = min(right_indices, key=arr.__getitem__, default=0)
        # Add that person to answer and recurse for next turn after
        # initializing that person at left side
        res = arr[person] + \
            find_min_time(leftmask | (1 << person), not turn, arr, n)
    else:
        # count total set bits in 'leftmask'
        if leftmask.bit_count() == 1:
            for i in range(n):
                # Since one person is present at left side, thus return that
                # person only
                if (leftmask & (1 << i)) != 0:
                    res = arr[i]
                    break
        else:
            # try for every pair of people by sending them to right side
            # Initialize the result with maximum value
            res = float('inf')
            for i in range(n):
                # If ith person is not present then skip the rest loop
                if (leftmask & (1 << i)) == 0:
                    continue
                for j in range(i+1, n):
                    if (leftmask & (1 << j)) != 0:
                        # Find maximum integer(slowest person's time)
                        val = max(arr[i], arr[j])
                        # Recurse for other people after un-setting the ith and
                        # jth bit of left-mask
                        val += find_min_time(
                            (leftmask ^ (1 << i) ^ (1 << j)), not turn, arr, n)
                        # Find minimum answer among all chosen values
                        res = min(res, val)

    return res

def find_time(arr, n):
    # Utility function to find minimum time
    # Find the mask of 'n' peoples
    leftmask = (1 << n) - 1

    # Initialize all entries in dp as -1
    for i in range((1 << 20)):
        dp[i][0] = -1
        dp[i][1] = -1

    return find_min_time(leftmask, False, arr, n)

arr = [10, 20, 30]
n = 3
result = find_time(arr, n)
assert result == 60
print(result)

# This code is contributed by lokeshmvs21.
# https://www.geeksforgeeks.org/program-bridge-torch-problem/
