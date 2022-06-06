from .__init__ import *


class Account:

    def __init__(self, json_packet: dict):
        self.user_account = json_packet
        self.user_profile = json_packet['profile']
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
        if not cursor.execute(f"SELECT * FROM sqlite_master WHERE type='table' AND name='{self.table_name}'").fetchall():
            cursor.execute(f"CREATE TABLE {self.table_name} ("
                           f"id text,"
                           f"login json,"
                           f"account json,"
                           f"room json,"
                           f"message json,"
                           f"notification json)")

        # check if account exists using username
        if not cursor.execute(f"SELECT * FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}'").fetchall():

            # HASH password
            self.user_account['password'] = bcrypt.hashpw(self.user_account["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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
                           f"null,"
                           f"null,"
                           f"null,"
                           f"null)", [str(id(self.username)), json.dumps(self.user_account)])
            database.commit()
            database.close()
            return {"result": account_generated_true}
        else:
            database.close()
            return {"result": account_exists_true}

    async def login(self):
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
                            "id": user[0],
                            "login": user[1],
                            "account": user_account_data,
                            "room": user[3],
                            "message": user[4],
                            "notification": user[5]
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
            TODO: """
            + use a faster algorithm to iterate over tables\
            and find one matching email & password.
            """
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()
            tables = cursor.execute(f"select name from sqlite_master").fetchall()

            index = 0
            for table in tables:
                matching_account = json.loads(cursor.execute(f"""
        SELECT * FROM {table[0]} WHERE json_extract(account, '$.email') = '{self.email}';
        """).fetchone()[0])

                # passwords
                input_password = self.password.encode('utf-8')
                local_password = matching_account['password'].encode('utf-8')

                index += 1  # increment index every account check

                # compare hashed passwords
                try:
                    if bcrypt.checkpw(input_password, local_password):
                        matching_account.pop('password')  # remove password
                        return {"result": account_access_granted, "account": matching_account}
                    else:
                        # declare password incorrect if index == tables
                        if index == len(tables):
                            return {"result": account_access_denied_password}
                except ValueError:
                    cursor.execute(f"DROP TABLE {self.username}")
                    database.commit()
                    return {"result": account_access_denied_passwordhash}
        else:
            return {"result": account_exists_false}

    async def authenticate(self):
        try:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            # passwords
            input_password = self.password.encode('utf-8')
            local_password: str = cursor.execute(f"""
            select json_extract(account, '$.password') from {self.username};
            """).fetchone()[0].encode('utf-8')

            # compare hashed passwords
            try:
                if bcrypt.checkpw(input_password, local_password):
                    return {"result": account_access_granted}
                else:
                    return {"result": account_access_denied_password}
            except ValueError:
                cursor.execute(f"DROP TABLE {self.username}")
                database.commit()
                return {"result": account_access_denied_passwordhash}

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
            cursor.execute(f"DROP TABLE {self.username}")
            database.commit()
            return {"result": account_deactivated_true}
        else:
            return authentication_result
