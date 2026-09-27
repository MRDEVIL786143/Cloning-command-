import argparse
import time


def main():
    parser = argparse.ArgumentParser(description='Safe sample terminal app')
    parser.add_argument('--count', type=int, default=5, help='How many lines to print')
    parser.add_argument('--name', default='cyber-user', help='Name to display')
    args = parser.parse_args()

    print('> cyber runner initialized')
    print(f'> operator: {args.name}')
    for i in range(1, args.count + 1):
        print(f'[{i}/{args.count}] running ...')
        time.sleep(1)
    print('> complete: task finished successfully')


if __name__ == '__main__':
    main()
