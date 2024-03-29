from .__init__ import *


class Search:

    def __init__(self, login_data: dict):
        self.account: dict = login_data
        self.username: str = self.account['username']
        self.email: str = self.account['email']
        self.password: str = self.account['password']

        # mongodb server connection
        self.mongodb_connection = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=500)

        # database user's account table
        self.table_name = users_table_name
        self.database_name = users_database_name

    async def search_room_by_title(self, room_title: str):
        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # if roomTitle is not empty
                if room_title:
                    # lowercase
                    room_title = room_title.lower()
                    # store specific rooms matching current room_title
                    matching_rooms = []
                    # get account with room matching title
                    # NOTICE: I want a better way to search through Mongodb as SQlite "LIKE" function
                    matching_documents = table.find({"rooms.title": room_title}, {"_id": 0, "rooms": {"$elemMatch": {"title": room_title}}})

                    # NOTICE: could not find a MongoDB function to simplify this code
                    for user_account in matching_documents:
                        for room in user_account['rooms']:
                            matching_rooms.append(room)

                    # if room exists
                    if matching_rooms:
                        return {"result": room_match_found, "rooms": matching_rooms}
                    else:
                        return {"result": room_exists_false}
                # just incase roomTitle reaches here while empty
                else:
                    return {"result": room_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}

    async def search_room_by_id(self, room_id: str):
        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # if roomId is not empty
                if room_id:
                    # get room with _id matching room_id
                    search_result = table.find_one({"rooms._id": room_id}, {"_id": 0, "rooms": {"$elemMatch": {"_id": room_id}}})

                    # check if search_result is true
                    # search_result will be true if not empty
                    if search_result:
                        # get room's author account
                        # search_result return data like this {'rooms':[]}
                        room_author = await self.search_user_by_id(search_result['rooms'][0]['author'])

                        # other keys are not required here
                        room_author_filtered = {
                            "_id": room_author['account']['_id'],
                            "username": room_author['account']['username'],
                            "email": room_author['account']['email'],
                            "displayName": room_author['account']['displayName']
                        }

                        matching_room = search_result['rooms'][0]
                        # set room's author to author's account
                        matching_room['author'] = room_author_filtered
                        return {"result": room_match_found, "room": matching_room}
                    else:
                        return {"result": room_exists_false}
                # just incase roomId reaches here while empty
                else:
                    return {"result": room_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}

    async def search_user_by_id(self, user_id: str):
        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # if userId is not empty
                if user_id:
                    # get user with _id matching user_id
                    matching_user: dict = table.find_one({"_id": user_id})

                    # check if search_result is true
                    if matching_user:
                        # remove password
                        matching_user.pop("password")
                        return {"result": user_match_found_true, "account": matching_user}
                    else:
                        return {"result": user_match_found_false}
                # just incase userId reaches here while empty
                else:
                    return {"result": account_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}

    async def search_friend_rooms(self):
        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # get current user's data from database
                local_user = table.find_one({"username": self.username})

                # check if user is following any other user
                try:
                    local_user['following']
                except KeyError:
                    return {"result": "you are not following any user"}

                # stores a list of rooms found from user's following
                rooms_found = []

                # search for document with matching "_id"
                for following_user_id in local_user['following']:

                    # get following user's account
                    following_user = await self.search_user_by_id(following_user_id)

                    if following_user['result'] == user_match_found_true:
                        # just incase key: rooms does not exist
                        try:
                            following_user['account']['rooms']
                        except KeyError:
                            following_user['account']['rooms'] = []

                        # store rooms found in one list "rooms_found"
                        for room in following_user['account']['rooms']:
                            # get room's author account
                            # other keys are not required here
                            room_author = {
                                "_id": following_user['account']['_id'],
                                "username": following_user['account']['username'],
                                "email": following_user['account']['email'],
                                "displayName": following_user['account']['displayName']
                            }
                            room['author'] = room_author
                            rooms_found.append(room)

                    elif following_user['result'] == user_match_found_false:
                        # remove "_id" of account that does not exist
                        table.update_one({"username": self.username}, {"$pull": {"following": following_user_id}})

                # if rooms were found
                if rooms_found:
                    return {"result": "rooms found: true", "rooms": rooms_found}
                else:
                    return {"result": "you follow users with 0 rooms"}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
