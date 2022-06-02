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
