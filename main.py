from __init__ import *


# server host address ws://HOST:PORT/
HOST: str = '0.0.0.0'
PORT: str = '5000'


websocket_connections: dict = {
    # "username": websocket
}


# server connection gateway
async def index(websocket):
    connected_username = str

    try:
        async for data in websocket:
            try:
                # decode 'data' to proper json or type(dict)
                json_packet: dict = json.loads(data)

                try:
                    namespace = json_packet['namespace']
                    user_account = json_packet['account']
                    connected_username = user_account['username']

                    # ENSURE: account values are not empty
                    try:
                        [user_account['email'], user_account['password'], user_account['username']]
                    except KeyError:
                        await websocket.send(str({"result": "empty account value"}))
                        await websocket.close()
                        return

                    # ENSURE: username is lowercase
                    user_account['username'] = user_account['username'].lower()

                    # ENSURE: username don't have unwanted characters
                    for char in user_account['username']:
                        # characters besides these are declared unwanted
                        chars: str = "abcdefghijklmnopqrstuvwxyz_0123456789"
                        if char not in chars:
                            await websocket.send(str({"result": username_unwanted_character}))
                            await websocket.close()
                            return

                    # handle namespace connection
                    if namespace:

                        # login
                        if namespace == '/':
                            authentication_result: dict = await Account(user_account).login()

                            if authentication_result['result'] == account_exists_false:
                                await websocket.send(str(authentication_result))
                                await websocket.close()
                            elif authentication_result['result'] == account_access_granted:
                                await websocket.send(str(authentication_result))
                                # add websocket to websocket_connections
                                websocket_connections[connected_username] = websocket
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

                        # update username
                        elif namespace == '/update/username':
                            try:
                                # ENSURE: updateUsername exists
                                update_username: str = json_packet['updateUsername']

                                # ENSURE: updateUsername is lowercase
                                update_username = update_username.lower()

                                if len(update_username) >= 5:
                                    if len(user_account['username']) >= 5:
                                        # ENSURE: updateUsername don't have unwanted characters
                                        for char in update_username:
                                            # characters besides these are declared unwanted
                                            chars: str = "abcdefghijklmnopqrstuvwxyz_0123456789"
                                            if char not in chars:
                                                await websocket.send(str({"result": username_unwanted_character}))
                                                await websocket.close()
                                                return

                                        update_result = await Account(user_account).update_username(update_username)
                                        await websocket.send(str(update_result))
                                        await websocket.close()
                                    else:
                                        # username is empty
                                        await websocket.send(str({"result": "username is length less than 5"}))
                                        await websocket.close()
                                else:
                                    # updateUsername is empty
                                    await websocket.send(str({"result": "updateUsername is length less than 5"}))
                                    await websocket.close()
                            # key: updateUsername does not exist
                            except KeyError:
                                await websocket.send(str({"result": "updateUsername is required"}))
                                await websocket.close()

                        # update password
                        elif namespace == '/update/password':
                            try:
                                # ENSURE: updatePassword exists
                                update_password: str = json_packet['updatePassword']

                                if len(update_password) >= 8:
                                    if len(user_account['username']) >= 5:
                                        update_result = await Account(user_account).update_password(update_password)
                                        await websocket.send(str(update_result))
                                        await websocket.close()
                                    else:
                                        # username is empty
                                        await websocket.send(str({"result": "username is length less than 5"}))
                                        await websocket.close()
                                else:
                                    # updatePassword is empty
                                    await websocket.send(str({"result": "updatePassword is length less than 8"}))
                                    await websocket.close()
                            # key: updatePassword does not exist
                            except KeyError:
                                await websocket.send(str({"result": "updatePassword is required"}))
                                await websocket.close()

                        # deactivate
                        elif namespace == '/deactivate':
                            authentication_result: dict = await Account(user_account).deactivate()

                            if authentication_result['result'] == account_exists_false:
                                await websocket.send(str(authentication_result))
                                await websocket.close()
                            elif authentication_result['result'] == account_deactivated_true:
                                # remove connected_username
                                if connected_username in websocket_connections:
                                    websocket_connections.pop(connected_username)

                                await websocket.send(str(authentication_result))
                                await websocket.close()
                            else:
                                await websocket.send(str(authentication_result))

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
        # remove connected_username
        if connected_username in websocket_connections:
            websocket_connections.pop(connected_username)


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
