from time import sleep


def main():
    for row in range(10):
        for col in range(10):
            # normally if '\n' as ending, print function flush by default
            # however, seems like it is not flushing when running in asyncio.subprocess
            # The code will print out every second only if flush=Ture
            # print('I am sleepy, sleeping for 1 sec.', flush=True)
            print(row * 10 + col, end=' ', flush=True)
            sleep(1)
        print('', end='\n', flush=True)


if __name__ == '__main__':
    main()
