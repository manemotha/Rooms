from .__init__ import *


class React:

    def __init__(self, login_data: dict):
        self.account: dict = login_data
        self.username: str = self.account['username']
        self.email: str = self.account['email']
        self.password: str = self.account['password']

        # mongodb server connection
        self.mongodb_connection = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=500)

        # database & user's account table
        self.table_name = users_table_name
        self.database_name = users_database_name

    async def like_room_by_id(self, target_room_id: str):
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:

                # check if target_room exists
                try:
                    matching_room = await Search(self.account).search_room_by_id(target_room_id)
                    # if target room does not exist. this will raise a KeyError exception
                    matching_room = matching_room['room']

                    # get current user's local account
                    current_user_id: str = table.find_one({"username": self.username})['_id']

                    # compare author id with current user's id
                    if matching_room['author'] != current_user_id:

                        # check if key: likes exists
                        # if not then create a placeholder to avoid exception KeyError
                        try:
                            matching_room['likes']
                        except KeyError:
                            matching_room['likes'] = []

                        # like room if not liked
                        if current_user_id not in matching_room['likes']:
                            # add current user's id to target user's follower
                            table.update_one({"rooms._id": target_room_id}, {"$push": {"rooms.$.likes": current_user_id}})

                            return {"result": liked_room_true}
                        # unlike room if already liked
                        else:
                            # remove current user's id from target user's followers
                            table.update_one({"rooms._id": target_room_id}, {"$pull": {"rooms.$.likes": current_user_id}})

                            return {"result": liked_room_false}

                    # if target_room_author matches current login _id
                    else:
                        return {"result": "you can not like your own room"}
                except KeyError:
                    return {"result": room_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}
