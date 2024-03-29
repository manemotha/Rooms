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
        self.table_name = users_table_name
        self.database_name = users_database_name

    async def signup(self):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()
        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
        # create database connection
        database = self.mongodb_connection[self.database_name]

        # connect to table
        table = database.get_collection(self.table_name)

        # account exists
        if table.find_one({"username": self.username}):
            return {"result": account_exists_true}
        else:
            # hash user password
            self.user_account['password']: bytes = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())
            self.user_account['_id'] = f"user-{uuid.uuid4().hex}"

            # create user account
            table.insert_one(self.user_account)

            return {"result": account_generated_true}

    async def login(self):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()
        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
        # create database connection
        database = self.mongodb_connection[self.database_name]

        # login with username
        if self.username:

            # ENSURE: Database table/collection exists
            try:
                table = database.get_collection(self.table_name)
            except TypeError:
                return {"result": account_exists_false}
            
            # passwords
            input_password = self.password.encode('utf-8')
            local_password: bytes = table.find_one({"username": self.username})["password"]

            # check if password is hashed
            try:
                bcrypt.checkpw(input_password, local_password)
            except ValueError:
                table.delete_one({"username": self.username})
                return {"result": account_access_denied_passwordhash}
            
            # compare hash passwords
            if bcrypt.checkpw(input_password, local_password):

                # user account
                user_account_data: dict = table.find_one({"username": self.username})

                # remove password for security purposes
                user_account_data.pop('password')

                return {"result": account_access_granted, "account": user_account_data}
            else:
                return {"result": account_access_denied_password}

        elif self.email:

            # ENSURE: Database table/collection exists
            try:
                table = database.get_collection(self.table_name)
            except pymongo.errors.CollectionInvalid:
                return  {"result": account_exists_false}
            
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

                    # group id & account column
                    result_account = {
                        "_id": result["_id"],
                        "username": result_account['username'],
                        "email": result_account['email'],
                        "diplayName": result_account['displayName']
                    }
                    accounts_found.append(result_account)
                
                # return all accounts matching emails for users to choose from and auto login with username
                return {"result": "multiple accounts with this email", "account": accounts_found}

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

                # check if password is hashed
                try:
                    bcrypt.checkpw(input_password, local_password)
                except ValueError:
                    table.delete_one({"username": self.username})
                    return {"result": account_access_denied_passwordhash}
                
                # compare hashed passwords
                if bcrypt.checkpw(input_password, local_password):
                    return {"result": account_access_granted, "account": user_account_data}
                else:
                    return {"result": account_access_denied_password}
                
            # users length == 0
            else:
                return {"result": account_exists_false}
        else:
            return {"result": account_exists_false}

    async def authenticate(self):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()
        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
        # create database connection
        database = self.mongodb_connection[self.database_name]

        # ENSURE: Database table/collection exists
        table = database.get_collection(self.table_name)

        # find account's password with username = self.username
        try:
            input_password = self.password.encode('utf-8')
            local_password = table.find_one({"username": self.username})["password"]
        except TypeError:
            return {"result": account_exists_false}
        
        # check if password is hashed
        try:
            bcrypt.checkpw(input_password, local_password)
        except ValueError:
            table.delete_one({"username": self.username})
            database.commit()
            return {"result": account_access_denied_passwordhash}
        
        # compare hashed passwords
        if bcrypt.checkpw(input_password, local_password):
            return {"result": account_access_granted}
        else:
            return {"result": account_access_denied_password}

    async def update_display_name(self, update_display_name):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()
        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
        # create database connection
        database = self.mongodb_connection[self.database_name]

        # connect to table
        table = database.get_collection(self.table_name)

        # if username is not empty
        if self.username:
            authentication_result = await self.authenticate()

            if authentication_result['result'] == account_access_granted:
                table.update_one({"username": self.username}, {"$set": {"displayName": update_display_name}})

                # get user data from database
                local_user_data = table.find_one({"username": self.username})

                # remove password for security purposes
                local_user_data.pop('password')
                return {"result": account_displayName_updated_true, "account": local_user_data}
            else:
                return authentication_result
        else:
            return {"result": account_exists_false}

    async def update_username(self, update_username: str):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()
        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
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
                else:
                    return {"result": account_updateUsername_exists_true}
            else:
                return authentication_result
        else:
            return {"result": account_exists_false}

    async def update_password(self, update_password: str):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()
        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
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

    async def deactivate(self):
        # test mongodb server connection
        try:
            self.mongodb_connection.server_info()

        except pymongo.errors.ConnectionFailure:
            return {"result": mongodb_connection_error}
        
        # user authentication
        authentication_result = await self.authenticate()

        if authentication_result['result'] == account_exists_false:
            return {"result": account_exists_false}
            
        elif authentication_result['result'] == account_access_granted:
            # create database connection
            database = self.mongodb_connection[self.database_name]

            # connect to table
            table = database.get_collection(self.table_name)

            # delete account
            table.delete_one({"username": self.username})
            
            return {"result": account_deactivated_true}
        else:
            return authentication_result
