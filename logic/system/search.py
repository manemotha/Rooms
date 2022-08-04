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
                    # store specific rooms matching current room_title
                    matching_rooms = []
                    # get account with room matching title
                    matching_documents = table.find({"rooms.title": room_title})

                    # iterate through user_account to return only matching rooms not full account
                    # NOTICE: could not find a MongoDB function to simplify this code
                    for user_account in matching_documents:
                        for room in user_account['rooms']:
                            if room_title == room['title']:
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
