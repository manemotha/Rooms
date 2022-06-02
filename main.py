from __init__ import *


# server host address ws://HOST:PORT/
HOST: str = '0.0.0.0'
PORT: str = '5000'


# server connection gateway
async def index(websocket, namespace: str):
    pass


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
