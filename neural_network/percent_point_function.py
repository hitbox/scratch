import argparse

def percent_point_function(sorted_numbers, percentile):
    n = len(sorted_numbers)
    index = (percentile / 100) * (n - 1)
    if index.is_integer():
        return sorted_numbers[int(index)]
    else:
        lower_index = int(index // 1)
        upper_index = lower_index + 1
        lower_value = sorted_numbers[lower_index]
        upper_value = sorted_numbers[upper_index]
        return lower_value + (index - lower_index) * (upper_value - lower_value)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('percentile', type=int)
    parser.add_argument('integers', nargs='+')
    args = parser.parse_args(argv)

    integers = sorted(map(int, args.integers))

    print(percent_point_function(integers, args.percentile))

if __name__ == '__main__':
    main()
