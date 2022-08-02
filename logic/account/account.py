import pymongo.errors

from .__init__ import *


class Account:

    def __init__(self, json_packet: dict):
        self.user_account = json_packet
        self.email: str = self.user_account['email']
        self.username: str = self.user_account['username']
        self.password: str = self.user_account['password']

        # mongodb server connection
        self.mongodb_connection = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=500)

        # database user's account table
        self.table_name = 'users'
        self.database_name = "demo"

    async def signup(self):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            # account exists
            if table.find_one({"username": self.username}):
                return {"result": account_exists_true}
            else:
                # hash user password
                self.user_account['password'] = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())
                # create user account
                table.insert_one(self.user_account)
                return {"result": account_generated_true}

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def login(self):
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # login with username
            if self.username:

                try:
                    # connect to table
                    table = database.get_collection(self.table_name)

                    # passwords
                    input_password = self.password.encode('utf-8')
                    local_password: str = table.find_one({"username": self.username})["password"]

                    # compare hashed passwords
                    try:
                        if bcrypt.checkpw(input_password, local_password):

                            # user account
                            user: dict = table.find_one({"username": self.username})

                            # convert user.account column to proper json/dict
                            user_account_data = user
                            user_account_data.pop('password')  # remove password for security purposes

                            return {"result": account_access_granted, "account": user_account_data}
                        else:
                            return {"result": account_access_denied_password}
                    # delete row/account if local password is not hashed
                    except ValueError:
                        table.delete_one({"username": self.username})
                        return {"result": account_access_denied_passwordhash}
                # database/table does not exist
                except TypeError:
                    return {"result": account_exists_false}

            elif self.email:

                try:
                    # connect to table
                    table = database.get_collection(self.table_name)

                    # user account
                    users = []
                    for user in table.find({"email": self.email}):
                        users.append(user)

                    # found many accounts
                    if len(users) > 1:
                        accounts_found = []
                        for result in users:
                            # account column
                            result_account: dict = result
                            result_account.pop('password')
                            print(result['_id'])

                            # group id & account column
                            result_account = {
                                "_id": result["_id"],
                                "username": result_account['username'],
                                "email": result_account['email'],
                                "diplayName": result_account['displayName']
                            }
                            accounts_found.append(result_account)
                        # return all accounts matching emails for users to choose from and auto login with username
                        return {"result": account_access_granted, "account": accounts_found}

                    # found one account
                    elif len(users) == 1:
                        # reassign variable
                        user = users[0]

                        # passwords
                        input_password = self.password.encode('utf-8')
                        local_password = user['password']

                        # convert user.account column to proper json/dict
                        user_account_data = user
                        user_account_data.pop('password')  # remove password for security purposes

                        # compare hashed passwords
                        try:
                            if bcrypt.checkpw(input_password, local_password):
                                return {"result": account_access_granted, "account": user_account_data}
                            else:
                                return {"result": account_access_denied_password}
                        except ValueError:
                            table.delete_one({"username": self.username})
                            return {"result": account_access_denied_passwordhash}
                    # users length == 0
                    else:
                        return {"result": account_exists_false}
                # collection / table does not exist
                except pymongo.errors.CollectionInvalid:
                    return  {"result": account_exists_false}
            else:
                return {"result": account_exists_false}
        # error connecting to mongodb server
        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def authenticate(self):
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            try:
                # passwords
                input_password = self.password.encode('utf-8')
                local_password = table.find_one({"username": self.username})["password"]

                # compare hashed passwords
                try:
                    if bcrypt.checkpw(input_password, local_password):
                        return {"result": account_access_granted}
                    else:
                        return {"result": account_access_denied_password}
                except ValueError:
                    table.delete_one({"username": self.username})
                    database.commit()
                    return {"result": account_access_denied_passwordhash}
            except TypeError:
                return {"result": account_exists_false}
        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def update_username(self, update_username: str):
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            # if username is not empty
            if self.username:
                authentication_result = await self.authenticate()

                if authentication_result['result'] == account_access_granted:

                    # check if account exists using update_username
                    if table.find_one({"username": update_username}) is None:
                        # get user data from database
                        local_user_data = table.find_one({"username": self.username})
                        # store new username into local_json_account
                        local_user_data['username'] = update_username
                        # update username
                        table.update_one({"username": self.username}, {"$set": {"username": update_username}})
                        # remove password for security purposes
                        local_user_data.pop('password')
                        return {"result": account_username_updated_true, "account": local_user_data}
                    # account using update_username already exists
                    else:
                        return {"result": account_updateUsername_exists_true}
                else:
                    return authentication_result
            # username is empty
            else:
                return {"result": account_exists_false}
        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def update_password(self, update_password: str):
        try:
            self.mongodb_connection.server_info()

            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            # if username is not empty
            if self.username:
                authentication_result = await self.authenticate()

                if authentication_result['result'] == account_access_granted:

                    # try authentication using update_password
                    # compare update_password with local_password
                    self.password = update_password
                    password_result = await self.authenticate()

                    # handle if update_password grants access
                    if password_result['result'] == account_access_granted:
                        return {"result": account_updatePassword_match_oldPassword}

                    # HASH password
                    hashed_update_password = bcrypt.hashpw(update_password.encode('utf-8'),
                                                          bcrypt.gensalt())
                    # sqlite update column: account
                    table.update_one({"username": self.username}, {"$set": {"password": hashed_update_password}})

                    # get user data from database
                    local_user_data = table.find_one({"username": self.username})
                    # remove password for security purposes
                    local_user_data.pop('password')
                    return {"result": account_password_update_true, "account": local_user_data}
                else:
                    return authentication_result
            # username is empty
            else:
                return {"result": account_exists_false}
        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def deactivate(self):
        authentication_result = await self.authenticate()

        if authentication_result['result'] == account_exists_false:
            return {"result": account_exists_false}
        elif authentication_result['result'] == account_access_granted:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            # delete table
            cursor.execute(f"DELETE FROM {self.table_name} WHERE json_extract("
                               f"account, '$.username')='{self.username}'")
            database.commit()
            return {"result": account_deactivated_true}
        else:
            return authentication_result
