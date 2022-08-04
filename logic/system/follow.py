from .__init__ import *


class Follow:

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

    async def follow_user_by_id(self, target_user_id: str):
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            # authenticate current login
            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # if target account exists
                if table.find_one({"_id": target_user_id}) is not None:
                    # get current user
                    current_user = table.find_one({"username": self.username})
                    # create an empty "following" key
                    # the "follower" key will be created by MongoDB's "$push"
                    try:
                        current_user['following']
                    except KeyError:
                        current_user['following'] = []

                    # follow user if not following
                    if target_user_id not in current_user['following']:
                        # add current user's id to target user's follower
                        table.update_one({"_id": target_user_id}, {"$push": {"follower": current_user['_id']}})

                        # add target user's id to current user's following
                        table.update_one({"username": self.username}, {"$push": {"following": target_user_id}})

                        return {"result": followed_user}
                    # unfollow user if already following
                    else:
                        # remove current user's id from target user's followers
                        table.update_one({"_id": target_user_id}, {"$pull": {"follower": current_user['_id']}})

                        # remove target user's id from current user's following
                        table.update_one({"username": self.username}, {"$pull": {"following": target_user_id}})

                        return {"result": unfollowed_user}
                # account does not exist
                else:
                    # remove deactivated account from following
                    # this won't raise an error if "target_user_id" does not exist in "following"
                    table.update_one({"username": self.username}, {"$pull": {"following": target_user_id}})
                    return {"result": following_account_exists_false}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}
