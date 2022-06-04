from .__init__ import *


class Account:

    def __init__(self, json_packet: dict):
        self.user_account = json_packet
        self.user_profile = json_packet['profile']
        self.email: str = self.user_account['email']
        self.username: str = self.user_account['username']
        self.password: str = self.user_account['password']

    async def signup(self):
        try:
            if not os.path.exists(database_directory):
                os.makedirs(database_directory)

            # create and open database file
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            # create user table from username
            cursor.execute(f"""
            CREATE TABLE {self.username} (account json) """)

            # HASH password
            self.user_account['password'] = bcrypt.hashpw(self.user_account["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # add values
            cursor.execute(f"insert into {self.username} values (?)", [json.dumps(self.user_account)])
            database.commit()
            return {"result": account_generated_true}

        except sqlite3.OperationalError:
            return {"result": account_exists_true}

    async def login(self):
        try:
            # login with username
            if self.username:
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

                        # user account
                        account_data: dict = json.loads(cursor.execute(f"""
                            select json_extract(account, '$') from {self.username};
                            """).fetchone()[0])
                        account_data.pop('password')  # remove password for security purposes

                        return {"result": account_access_granted, "account": account_data}
                    else:
                        return {"result": account_access_denied_password}
                except ValueError:
                    cursor.execute(f"DROP TABLE {self.username}")
                    database.commit()
                    return {"result": account_access_denied_passwordhash}

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

        except sqlite3.OperationalError:
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
