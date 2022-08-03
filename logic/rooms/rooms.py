from .__init__ import *


class Rooms:

    def __init__(self, login_data: dict):
        self.account: dict = login_data
        self.username: str = self.account['username']
        self.email: str = self.account['email']
        self.password: str = self.account['password']
        self.table_name: str = users_table_name

        # mongodb server connection
        self.mongodb_connection = pymongo.MongoClient(database_uri, serverSelectionTimeoutMS=500)

        # database user's account table
        self.table_name = users_table_name
        self.database_name = users_database_name

    async def new_room(self, room: dict):
        # generate unique id from room-title
        # this id is used for CRUD functionalities on this room
        room['id']: str = str(id(room['title']))

        try:
            self.mongodb_connection.server_info()
            # create database connection
            database = self.mongodb_connection[self.database_name]
            # connect to table
            table = database.get_collection(self.table_name)

            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # update / create new room value
                table.update_one({"username": self.username}, {"$push": {"rooms": room}})

                # get all local rooms
                local_rooms: list = table.find_one({"username": self.username})["rooms"]

                return {"result": room_generated_true, "rooms": local_rooms}
            else:
                return authentication_result

        except pymongo.errors.ConnectionFailure:
            return {"result": "error connecting to mongodb database"}

    async def delete(self, room_id: str):
        try:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:

                # if roomId is not empty
                if room_id:
                    # check if room exists
                    if cursor.execute(f"""
                    SELECT json_extract(room, '$.{room_id}') FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}';
                    """).fetchone()[0]:
                        # get all local rooms
                        local_rooms: dict = json.loads(cursor.execute(f"""
                        SELECT json_extract(room, '$') FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}';
                        """).fetchone()[0])

                        # pop room matching room_id
                        local_rooms.pop(room_id)

                        # update room column
                        cursor.execute(f"UPDATE {self.table_name} SET room='{json.dumps(local_rooms)}' WHERE json_extract(account, '$.username')='{self.username}'")
                        database.commit()
                        database.close()
                        return {"result": room_deleted_true, "rooms": local_rooms}
                    else:
                        return {"result": room_exists_false}
                else:
                    return {"result": room_exists_false}
            else:
                return authentication_result
        # database/table does not exist
        except sqlite3.OperationalError:
            return {"result": account_exists_false}
