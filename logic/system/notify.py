from .__init__ import *


class Notify:

    def __init__(self, login_data: dict):
        self.account: dict = login_data
        self.username: str = self.account['username']
        self.email: str = self.account['email']
        self.password: str = self.account['password']

        # mongodb server connection
        self.mongodb_connection = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=500)

        # database user's account table
        self.table_name: str = users_table_name
        self.database_name: str = users_database_name

    async def websocket_notification(self, message: str):
        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                local_user_data: dict = table.find_one({"username": self.username})

                # check if key "followers" exists
                try:
                    local_user_data['follower']
                except KeyError:
                    local_user_data['follower'] = []

                if len(local_user_data['follower']) > 0:
                    # store all online/connected followers
                    connected_followers = []
                    # find all user's followers from database
                    for follower in local_user_data['follower']:
                        try:
                            # this raises a KeyError if follower is not online/connected
                            connected_followers.append(connected_accounts[follower])
                        except KeyError:
                            pass

                    # send notification to online followers
                    # this sends a websocket message to followers to reload data
                    if connected_followers:
                        websockets.broadcast(connected_followers, json.dumps({"result": message}))
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}
