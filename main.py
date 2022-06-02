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
                    user_account = json_packet['account']
                    user_profile = user_account['profile']

                    # handle namespace connection
                    if namespace:

                        # login
                        if namespace == '/':
                            authentication_result: dict = await Account(user_account).login()

                            if authentication_result['result'] == account_exists_false:
                                await websocket.send(str(authentication_result))
                                await websocket.close()
                            elif authentication_result['result'] == account_access_granted:
                                await websocket.send(str(authentication_result['result']))
                            else:
                                await websocket.send(str(authentication_result))

                        # signup
                        elif namespace == '/signup':
                            if len(user_account['username']) >= 5:
                                if user_account['email']:
                                    TODO: "email address verification"
                                    if len(user_account['password']) >= 8:
                                        signup_result: dict = await Account(user_account).signup()

                                        if user_account['username'] != "":
                                            if signup_result['result'] == account_exists_true:
                                                await websocket.send(str(signup_result))
                                                await websocket.close()
                                            elif signup_result['result'] == username_unwanted_character:
                                                await websocket.send(str(signup_result))
                                                await websocket.close()
                                            else:
                                                await websocket.send(str(signup_result))
                                                await websocket.close()
                                    else:
                                        # password < 8
                                        await websocket.send(str({"result": "password is length less than 8"}))
                                        await websocket.close()
                                else:
                                    # email is empty
                                    await websocket.send(str({"result": "email is empty"}))
                                    await websocket.close()
                            else:
                                # username < 5
                                await websocket.send(str({"result": "username is length less than 5"}))
                                await websocket.close()

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
