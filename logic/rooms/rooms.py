from .__init__ import *


class Rooms:

    def __init__(self, login_data: dict):
        self.account: dict = login_data
        self.username: str = self.account['username']
        self.email: str = self.account['email']
        self.password: str = self.account['password']
        self.table_name: str = users_table_name

        # mongodb server connection
        self.mongodb_connection = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=500)

        # database user's account table
        self.table_name = users_table_name
        self.database_name = users_database_name

    async def new_room(self, room: dict):

        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # lowercase
                room_title = room['title'].lower()
                room['title']: str = room_title
                # generate unique id from room-title
                # this id is used for CRUD functionalities on this room
                room['_id']: str = f"room-{uuid.uuid4().hex}"
                # use user_id for room authorId
                room['author']: str = table.find_one({"username": self.username})['_id']

                # update / create new room value
                table.update_one({"username": self.username}, {"$push": {"rooms": room}})

                # get all local rooms
                local_rooms: list = table.find_one({"username": self.username})["rooms"]

                return {"result": room_generated_true, "rooms": local_rooms}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def delete(self, room_id: str):
        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:

                # if roomId is not empty
                if room_id:
                    # try to remove room
                    updated_room_result = table.update_one({"username": self.username}, {"$pull": {"rooms": {"_id": room_id}}})
                    # confirm if room existed or was removed
                    if updated_room_result.raw_result['nModified'] == 1:
                        # get all local rooms
                        local_rooms: dict = table.find_one({"username": self.username})["rooms"]
                        return {"result": room_deleted_true, "rooms": local_rooms}
                    else:
                        return {"result": room_exists_false}
                else:
                    return {"result": room_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}
