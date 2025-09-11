import argparse
import logging

from math import inf

logger = logging.getLogger('coin_change')

def change_recursive(amount, coins):
    logger.info('amount=%r, coins=%r', amount, coins)
    if amount == 0:
        logger.info('base case')
        return (0, [])
    elif amount < 0:
        logger.info('invalid case')
        return (inf, [])

    best_count = inf
    best_combo = []
    for coin in coins:
        count, combo = change_recursive(amount - coin, coins)
        if count + 1 < best_count:
            best_count = count + 1
            best_combo = combo + [coin]

    logger.info('result found. best_count=%r, best_combo=%r', best_count, best_combo)
    return (best_count, best_combo)

def change_dp(amount, coins):
    """
    Return a list of the least amount of coins to make amount.
    """
    logger.info('amount=%r, coins=%r', amount, coins)
    # dp[i] = minimum number of coins to make amount i
    dp = [inf] * (amount + 1)
    logger.info('dp=%r', dp)

    # parent[i] = coin chosen to reach amount i optimally
    parent = [-1] * (amount + 1)
    logger.info('parent=%r', parent)

    dp[0] = 0
    logger.info('finding least amount of coins for amount')
    logger.info('dp[0]=%r', dp[0])
    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0 and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1
                logger.info(
                    'i=%r, coin=%r, dp[%r] = dp[%r - %r] + 1 == %r',
                    i, coin, i, i, i-coin, dp[i])
                parent[i] = coin
    logger.info('after main loop')
    logger.info('dp=%r', dp)
    logger.info('dp[%r]=%r', amount, dp[amount])
    logger.info('parent=%r', parent)

    if dp[amount] == inf:
        # No solution possible
        return None

    # reconstruct coins
    logger.info('reconstructing coins')
    result = []
    cur = amount
    while cur > 0:
        coin = parent[cur]
        logger.info('cur=%r, coin=%r', cur, coin)
        result.append(coin)
        logger.info('result=%r', result)
        cur -= coin

    return (dp[amount], result)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('amount', type=int)
    parser.add_argument('coins', nargs='+', type=int)
    parser.add_argument('--recur', action='store_true', help='Recursively')
    parser.add_argument('--info', action='store_const', const=logging.INFO)
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.info)

    # Example amount = 37
    #         coins = [10, 9, 1]
    # == [9, 9, 9, 10]

    if args.recur:
        change_func = change_recursive
    else:
        change_func = change_dp

    best_count, best_combo = change_func(args.amount, args.coins)
    print(best_combo)

if __name__ == '__main__':
    main()
