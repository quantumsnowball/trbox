import asyncio

import websockets


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


async def main():
    async with websockets.serve(echo, "0.0.0.0", 5000):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
