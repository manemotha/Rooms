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
            return {"result": "error connecting to mongodb database"}

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
                        matching_room = search_result['rooms'][0]
                        return {"result": room_match_found, "room": matching_room}
                    else:
                        return {"result": room_exists_false}
                # just incase roomId reaches here while empty
                else:
                    return {"result": room_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

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
                    # remove password
                    matching_user.pop("password")

                    # check if search_result is true
                    if matching_user:
                        return {"result": "user match found: true", "account": matching_user}
                    else:
                        return {"result": account_exists_false}
                # just incase userId reaches here while empty
                else:
                    return {"result": account_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

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

                # if user is following other users
                if local_user['following']:
                    rooms_found = []

                    # search for document with matching "_id"
                    for following_user_id in local_user['following']:

                        # get following user's account
                        following_user = await self.search_user_by_id(following_user_id)

                        # just incase key: rooms does not exist
                        try:
                            following_user['account']['rooms']
                        except KeyError:
                            following_user['account']['rooms'] = []

                        # store rooms found in one list "rooms_found"
                        for room in following_user['account']['rooms']:
                            rooms_found.append(room)

                    # if rooms were found
                    if rooms_found:
                        return {"result": "rooms found: true", "rooms": rooms_found}
                    else:
                        return {"result": "you are not following any user"}
                else:
                    return {"result": "you are not following any user"}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}
