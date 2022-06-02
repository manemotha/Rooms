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
                            select json_extract(account, '$') from {self.user_account['username']};
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
                + login with email instead of username if username is empty;
                + iterate tables and find one that matches email & password;
                """
                pass

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
