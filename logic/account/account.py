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

            # create table if table does not exist
            try:
                database.create_collection(self.table_name)
            # table exists
            except pymongo.errors.CollectionInvalid:
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
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            try:
                # passwords
                input_password = self.password.encode('utf-8')
                local_password: str = cursor.execute(f"""
                SELECT json_extract(account, '$.password') FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}';
                """).fetchone()[0].encode('utf-8')

                # compare hashed passwords
                try:
                    if bcrypt.checkpw(input_password, local_password):
                        return {"result": account_access_granted}
                    else:
                        return {"result": account_access_denied_password}
                except ValueError:
                    cursor.execute(f"DELETE FROM {self.table_name} WHERE json_extract("
                                   f"account, '$.username')='{self.username}'")
                    database.commit()
                    return {"result": account_access_denied_passwordhash}
            except TypeError:
                return {"result": account_exists_false}
        except sqlite3.OperationalError:
            return {"result": account_exists_false}

    async def update_username(self, update_username: str):
        try:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            # if username is not empty
            if self.username:
                authentication_result = await self.authenticate()

                if authentication_result['result'] == account_access_granted:

                    # check if account exists using update_username
                    if not cursor.execute(f"SELECT * FROM {self.table_name} WHERE "
                                          f"json_extract(account, '$.username')='{update_username}'").fetchall():

                        # sqlite get user data from database
                        local_user_data = cursor.execute(f"SELECT * FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}'").fetchone()
                        # convert account column to proper json/dict
                        local_json_account = json.loads(local_user_data[2])

                        # store new username into local_json_account
                        local_json_account['username'] = update_username

                        # sqlite update username
                        cursor.execute(f"UPDATE {self.table_name} SET account='{json.dumps(local_json_account)}' WHERE json_extract(account, '$.username')='{self.username}'")

                        # save changes
                        database.commit()

                        # remove password for security purposes
                        local_json_account.pop('password')

                        # group all columns into one json/dict
                        user_data = {
                            "id": local_user_data[0],
                            "login": local_user_data[1],
                            "account": local_json_account,
                            "room": local_user_data[3],
                            "message": local_user_data[4],
                            "notification": local_user_data[5]
                        }
                        return {"result": account_username_updated_true, "account": user_data}
                    # account using update_username already exists
                    else:
                        return {"result": account_updateUsername_exists_true}
                else:
                    return authentication_result
            # username is empty
            else:
                return {"result": account_exists_false}
        # database/table does not exist
        except sqlite3.OperationalError:
            return {"result": account_exists_false}

    async def update_password(self, update_password: str):
        try:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

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

                    # sqlite get user data from database
                    local_user_data = cursor.execute(f"SELECT * FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}'").fetchone()
                    # convert account column to proper json/dict
                    local_json_account = json.loads(local_user_data[2])

                    # HASH password
                    local_json_account['password'] = bcrypt.hashpw(update_password.encode('utf-8'),
                                                          bcrypt.gensalt()).decode('utf-8')

                    # sqlite update column: account
                    cursor.execute(f"UPDATE {self.table_name} SET account='{json.dumps(local_json_account)}' WHERE json_extract(account, '$.username')='{self.username}'")

                    # save changes
                    database.commit()

                    # remove password for security purposes
                    local_json_account.pop('password')

                    # group all columns into one json/dict
                    user_data = {
                        "id": local_user_data[0],
                        "login": local_user_data[1],
                        "account": local_json_account,
                        "room": local_user_data[3],
                        "message": local_user_data[4],
                        "notification": local_user_data[5]
                    }
                    return {"result": account_password_update_true, "account": user_data}
                else:
                    return authentication_result
            # username is empty
            else:
                return {"result": account_exists_false}
        # database/table does not exist
        except sqlite3.OperationalError:
            return {"result": account_exists_false}

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
