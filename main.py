import json

import websockets.exceptions

from __init__ import *


# server host address ws://HOST:PORT/
HOST: str = '0.0.0.0'
PORT: str = '5000'


# server connection gateway
async def index(websocket):
    websocket_address: tuple = websocket.remote_address

    try:
        async for data in websocket:
            try:
                # decode 'data' to proper json or type(dict)
                json_packet: dict = json.loads(data)

                try:
                    namespace = json_packet['namespace']

                    if namespace:
                        pass
                    else:
                        await websocket.send(str({'result': 'unknown namespace'}))
                        await websocket.close()

                # json key error in json_packet
                except KeyError as error:
                    await websocket.send(str({'result': f'json error: {error}'}))
                    await websocket.close()

            # error decoding data: is not proper json
            except json.decoder.JSONDecodeError as error:
                await websocket.send(str({'result': f'json error: {error}'}))
                await websocket.close()

    # client disconnected
    except websockets.exceptions.ConnectionClosedError:
        print(websocket_address, 'disconnected')


# application server
async def server():
    async with websockets.serve(index, HOST, PORT):
        await asyncio.Future()  # run forever


# start application server
if __name__ == '__main__':
    try:
        print(f'[SERVER]: Listening on -> ws://{HOST}:{PORT}/')
        asyncio.run(server())
    except KeyboardInterrupt:
        print('\n[SERVER]: Server forced to stop')
