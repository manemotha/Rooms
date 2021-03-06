from .__init__ import *


class Account:

    def __init__(self, json_packet: dict):
        self.user_account = json_packet
        self.email: str = self.user_account['email']
        self.username: str = self.user_account['username']
        self.password: str = self.user_account['password']

        # database user's account table
        self.table_name = 'users'

    async def signup(self):
        # if database_directory does not exist
        if not os.path.exists(database_directory):
            os.makedirs(database_directory)

        # create and open database file
        database = sqlite3.connect(f'{database_directory}/accounts.db')
        cursor = database.cursor()

        # create database table if not exists
        if not cursor.execute(
                f"SELECT * FROM sqlite_master WHERE type='table' AND name='{self.table_name}'").fetchall():
            cursor.execute(f"CREATE TABLE {self.table_name} ("
                           f"id text,"
                           f"login json,"
                           f"account json,"
                           f"room json,"
                           f"message json,"
                           f"notification json)")

        # check if account exists using username
        if not cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}'").fetchall():

            # HASH password
            self.user_account['password'] = bcrypt.hashpw(self.user_account["password"].encode('utf-8'),
                                                          bcrypt.gensalt()).decode('utf-8')

            # add values
            cursor.execute(f"INSERT INTO {self.table_name} "
                           f"(id,"
                           f"account,"
                           f"login,"
                           f"room,"
                           f"message,"
                           f"notification) VALUES "
                           f"(?,"
                           f"?,"
                           f"?,"
                           f"?,"
                           f"?,"
                           f"?)", [str(id(self.username)), json.dumps(self.user_account), json.dumps({}), json.dumps({}), json.dumps(
                {}), json.dumps({})])
            database.commit()
            database.close()
            return {"result": account_generated_true}
        else:
            database.close()
            return {"result": account_exists_true}

    async def login(self):
        try:
            # login with username
            if self.username:
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

                            # user account
                            user: dict = cursor.execute(f"""
                                SELECT * FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}';
                                """).fetchone()

                            # convert user.account column to proper json/dict
                            user_account_data = json.loads(user[2])
                            user_account_data.pop('password')  # remove password for security purposes

                            # group all column into one json/dict
                            user_data = {
                                "id": json.loads(user[0]),
                                "login": json.loads(user[1]),
                                "account": user_account_data,
                                "room": json.loads(user[3]),
                                "message": json.loads(user[4]),
                                "notification": json.loads(user[5])
                            }

                            return {"result": account_access_granted, "account": user_data}
                        else:
                            return {"result": account_access_denied_password}
                    # delete row/account if local password is not hashed
                    except ValueError:
                        cursor.execute(f"DELETE FROM {self.table_name} WHERE json_extract("
                                       f"account, '$.username')='{self.username}'")
                        database.commit()
                        return {"result": account_access_denied_passwordhash}
                # database/table does not exist
                except TypeError:
                    return {"result": account_exists_false}

            elif self.email:
                database = sqlite3.connect(f'{database_directory}/accounts.db')
                cursor = database.cursor()

                # user account
                users: list = cursor.execute(f"""
                    SELECT * FROM {self.table_name} WHERE json_extract(account, '$.email')='{self.email}';
                    """).fetchall()

                # found many accounts
                if len(users) > 1:
                    accounts_found = []
                    for result in users:
                        # account column
                        result_account: dict = json.loads(result[2])
                        result_account.pop('password')

                        # group id & account column
                        result_account = {
                            "id": result[0],
                            "username": result_account['username'],
                            "email": result_account['email'],
                            "diplayName": result_account['displayName']
                        }
                        accounts_found.append(result_account)
                    # return all accounts matching emails for users to choose from and auto login with username
                    return {"result": account_access_granted, "account": accounts_found}

                # found one account
                elif len(users) == 1:
                    # navigate to account column index:2
                    user: str = users[0]

                    # passwords
                    input_password = self.password.encode('utf-8')
                    local_password: str = json.loads(user[2])['password'].encode('utf-8')

                    # convert user.account column to proper json/dict
                    user_account_data = json.loads(user[2])
                    user_account_data.pop('password')  # remove password for security purposes

                    # group all column into one json/dict
                    user_data = {
                        "id": user[0],
                        "login": user[1],
                        "account": user_account_data,
                        "room": user[3],
                        "message": user[4],
                        "notification": user[5]
                    }

                    # compare hashed passwords
                    try:
                        if bcrypt.checkpw(input_password, local_password):
                            return {"result": account_access_granted, "account": user_data}
                        else:
                            return {"result": account_access_denied_password}
                    except ValueError:
                        cursor.execute(f"DELETE FROM {self.table_name} WHERE json_extract("
                                       f"account, '$.username')='{self.username}'")
                        database.commit()
                        return {"result": account_access_denied_passwordhash}
                # users length == 0
                else:
                    return {"result": account_exists_false}
            else:
                return {"result": account_exists_false}
        # database/table does not exist
        except sqlite3.OperationalError:
            return {"result": account_exists_false}

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
                    return {"result": account_username_updated_true, "account": user_data}
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

        TODO: "schedule account for deactivation after 30 days"

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
