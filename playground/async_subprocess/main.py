import asyncio


async def job():
    cmd = 'python tests/playground/async_subprocess/long_task.py'
    process = await asyncio.create_subprocess_shell(cmd,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    print('finish creating process, this print immediately')

    # stdout, stderr = await process.communicate()
    # print(stdout, stderr)
    # print('finish communicate, this print after 10 seconds, blocking')

    # this gets output immediately when a line is ready:
    # still not print anything if no \n
    # if process.stdout:
    #     async for line in process.stdout:
    #         print(line.decode())

    # both the main function and coroutine need to flush to truly print immeditely
    while process.stdout:
        byte = await process.stdout.read(1)
        print(byte.decode(), end='', flush=True)


def main():
    asyncio.run(job())


if __name__ == '__main__':
    main()
