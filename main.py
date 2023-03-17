from __init__ import *

# server host address ws://HOST:PORT/
HOST: str = '0.0.0.0'
PORT: int = 4300


# server connection gateway
async def index(websocket):
    account_id = str

    try:
        async for data in websocket:

            # try decoding [data] to proper json or type(dict)
            try:
                json_packet: dict = json.loads(data)
            except json.decoder.JSONDecodeError as error:
                await websocket.send(json.dumps({'result': f'json error: {error}'}))
                await websocket.close()
                break

            # confirm if there's keys "namespace" and "account"
            try:
                namespace = json_packet['namespace'].lower()
                user_account = json_packet['account']
            except KeyError as error:
                await websocket.send(json.dumps({'result': f'json error: {error}'}))
                await websocket.close()
                break

            # ENSURE: account values are not empty
            try:
                [user_account['email'], user_account['password'], user_account['username']]
            except KeyError:
                await websocket.send(json.dumps({"result": "empty account value"}))
                await websocket.close()
                break

            # ENSURE: username is lowercase
            user_account['username'] = user_account['username'].lower()

            # ENSURE: username don't have unwanted characters
            for char in user_account['username']:
                # characters besides these are declared unwanted
                chars: str = "abcdefghijklmnopqrstuvwxyz_0123456789"
                if char not in chars:
                    await websocket.send(json.dumps({"result": username_unwanted_character}))
                    await websocket.close()
                    break

            try:
                # handle namespace connection
                if namespace:

                    # login
                    if namespace == login_namespace:
                        authentication_result: dict = await Account(user_account).login()

                        if authentication_result['result'] == account_exists_false:
                            await websocket.send(json.dumps(authentication_result))
                            await websocket.close()
                        elif authentication_result['result'] == account_access_granted:
                            # found one account using either username / email
                            try:
                                account_id = authentication_result['account']['_id']
                            except TypeError:
                                # found multiple accounts using email
                                # TODO: return accounts with same email
                                pass

                            # add websocket to connected_accounts
                            connected_accounts[account_id] = websocket
                            # send response to the server
                            await websocket.send(json.dumps(authentication_result))
                        else:
                            await websocket.send(json.dumps(authentication_result))

                    else:
                        # ensure username is >= 5
                        if len(user_account['username']) >= 5:
                            # ensure username is less than 15 characters
                            if len(user_account['username']) < 15:

                                # ----------- ACCOUNT NAMESPACES -----------
                                if namespace == signup_namespace:
                                    # ensure email is not empty
                                    if user_account['email']:
                                        # ensure password is not less than 8 chars
                                        if len(user_account['password']) >= 8:

                                            # ensure displayName exists
                                            try:
                                                user_account['displayName']
                                            except KeyError:
                                                await websocket.send(json.dumps({"result": "displayName is required"}))
                                                break

                                            signup_result: dict = await Account(user_account).signup()

                                            if signup_result['result'] == account_generated_true:
                                                await websocket.send(json.dumps(signup_result))
                                            elif signup_result['result'] == username_unwanted_character:
                                                await websocket.send(json.dumps(signup_result))
                                            else:
                                                await websocket.send(json.dumps(signup_result))

                                        else:
                                            # password < 8
                                            await websocket.send(json.dumps({"result": "password is length less than 8"}))
                                    else:
                                        # email is empty
                                        await websocket.send(json.dumps({"result": "email is empty"}))

                                # update displayName
                                elif namespace == update_displayname_namespace:

                                    # ENSURE: updateDisplayName exists
                                    try:
                                        update_display_name: str = json_packet['updateDisplayName']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "updateDisplayName is required"}))

                                    # ENSURE: updateDisplayName is not empty
                                    if update_display_name:
                                        update_result = await Account(user_account).update_display_name(update_display_name)
                                        await websocket.send(json.dumps(update_result))
                                    else:
                                        await websocket.send(json.dumps({"result": "updateDisplayName is empty"}))

                                # update username
                                elif namespace == update_username_namespace:
                                    
                                    # ENSURE: updateUsername exists
                                    try:
                                        update_username: str = json_packet['updateUsername']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "updateUsername is required"}))
                                        break

                                    # ENSURE: updateUsername is lowercase
                                    update_username = update_username.lower()

                                    if len(update_username) >= 5:
                                        # ENSURE: updateUsername don't have unwanted characters
                                        for char in update_username:
                                            # characters besides these are unwanted
                                            chars: str = "abcdefghijklmnopqrstuvwxyz_0123456789"
                                            if char not in chars:
                                                await websocket.send(json.dumps({"result": username_unwanted_character}))
                                                break

                                        update_result = await Account(user_account).update_username(update_username)
                                        await websocket.send(json.dumps(update_result))
                                    else:
                                        # updateUsername is not >= 5
                                        await websocket.send(json.dumps({"result": "updateUsername is length less than 5"}))

                                # update password
                                elif namespace == update_password_namespace:

                                    # ENSURE: updatePassword exists
                                    try:
                                        update_password: str = json_packet['updatePassword']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "updatePassword is required"}))

                                    # ENSURE: password is >= 8
                                    if len(update_password) >= 8:
                                        update_result = await Account(user_account).update_password(update_password)
                                        await websocket.send(json.dumps(update_result))
                                    else:
                                        await websocket.send(json.dumps({"result": "updatePassword is length less than 8"}))

                                # deactivate
                                elif namespace == deactivate_namespace:
                                    authentication_result: dict = await Account(user_account).deactivate()

                                    if authentication_result['result'] == account_exists_false:
                                        await websocket.send(json.dumps(authentication_result))
                                    elif authentication_result['result'] == account_deactivated_true:
                                        # remove connected_username
                                        if account_id in connected_accounts:
                                            connected_accounts.pop(account_id)

                                        await websocket.send(json.dumps(authentication_result))
                                    else:
                                        await websocket.send(json.dumps(authentication_result))

                                # ------------ ROOM NAMESPACES ------------
                                elif namespace == new_room_namespace:

                                    # ENSURE: room exists
                                    try:
                                        room: dict = json_packet['room']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "room is required"}))
                                        break

                                    # ENSURE: room has a title
                                    try:
                                        room_title: dict = json_packet['room']['title']

                                        update_result = await Rooms(user_account).new_room(room)
                                        await websocket.send(json.dumps(update_result))
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "room title is required"}))
                                        break

                                elif namespace == delete_room_namespace:

                                    # ENSURE: room exists
                                    try:
                                        room_id: str = json_packet['roomId']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "roomId is required"}))
                                        break

                                    update_result = await Rooms(user_account).delete(room_id)
                                    await websocket.send(json.dumps(update_result))

                                # ------------ SYSTEM NAMESPACES ------------
                                elif namespace == search_room_by_title_namespace:

                                    # ENSURE: roomTitle exists
                                    try:
                                        room_title: str = json_packet['roomTitle']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "roomTitle is required"}))
                                        break

                                    search_result = await Search(user_account).search_room_by_title(room_title)
                                    await websocket.send(json.dumps(search_result))

                                # SEARCH USER ROOM BY ID
                                elif namespace == search_room_by_id_namespace:

                                    # ENSURE: roomId exists
                                    try:
                                        room_id: str = json_packet['roomId']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "roomId is required"}))
                                        break

                                    search_result = await Search(user_account).search_room_by_id(room_id)
                                    await websocket.send(json.dumps(search_result))

                                # SEARCH USER BY ID
                                elif namespace == search_user_by_id_namespace:

                                    # ENSURE: userId exists
                                    try:
                                        user_id: str = json_packet['userId']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "userId is required"}))
                                        break

                                    search_result = await Search(user_account).search_user_by_id(user_id)
                                    await websocket.send(json.dumps(search_result))

                                # SEARCH ROOMS OF USERS FOLLOWED BY THIS USER
                                elif namespace == search_friend_rooms_namespace:
                                    search_result = await Search(user_account).search_friend_rooms()
                                    await websocket.send(json.dumps(search_result))

                                # FOLLOW & UNFOLLOW USER
                                elif namespace == follow_user_namespace:

                                    # ENSURE: userId exists
                                    try:
                                        user_id: str = json_packet['userId']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "userId is required"}))
                                        break

                                    follow_result = await Follow(user_account).follow_user_by_id(user_id)
                                    await websocket.send(json.dumps(follow_result))

                                # LIKE & UNLIKE ROOM
                                elif namespace == like_room_namespace:

                                    # ENSURE: roomId exists
                                    try:
                                        room_id: str = json_packet['roomId']
                                    except KeyError:
                                        await websocket.send(json.dumps({"result": "roomId is required"}))

                                    react_result = await React(user_account).like_room_by_id(room_id)
                                    await websocket.send(json.dumps(react_result))

                                # unknown namespace
                                else:
                                    await websocket.send(json.dumps({'result': unknown_namespace}))
                            else:
                                # username is greater than 15
                                await websocket.send(json.dumps({"result": "username is length greater than 15"}))
                        else:
                            # username is less than 5
                            await websocket.send(json.dumps({"result": "username is length less than 5"}))
                # unknown namespace
                else:
                    await websocket.send(json.dumps({'result': unknown_namespace}))
                    await websocket.close()

            except websockets.exceptions.ConnectionClosedOK:
                # user's websocket connection is closed
                # remove connected_id
                if account_id in connected_accounts:
                    connected_accounts.pop(account_id)

    # client disconnected
    except websockets.exceptions.ConnectionClosedError:
        # remove connected_username
        if account_id in connected_accounts:
            connected_accounts.pop(account_id)


# application server
async def server():
    async with websockets.serve(index, HOST, PORT):
        await asyncio.Future()  # run forever

# start application server
if __name__ == '__main__':
    try:
        print(f'[Rooms]: Listening on -> ws://{HOST}:{PORT}/')
    except KeyboardInterrupt:
        print('\n[Rooms]: Server forced to stop')

    # handle OSError when attempting to run server on an open Port
    try:
        asyncio.run(server())
    except OSError as error:
        print(f"[Rooms]: PORT:{PORT} is in use, Change to an offline port")
