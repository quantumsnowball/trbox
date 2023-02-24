import asyncio

import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:7000/api/ws') as ws:

            await ws.send_str('hello can you read me?')

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        # await ws.send_str(msg.data + '/answer')
                        pass
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

if __name__ == '__main__':
    asyncio.run(main())
