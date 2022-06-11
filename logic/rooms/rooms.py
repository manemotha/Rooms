from .__init__ import *


class Rooms:

    def __init__(self, login_data: dict, room: dict):
        self.account: dict = login_data
        self.username = self.account['username']
        self.email = self.account['email']
        self.password = self.account['password']
        self.room: dict = room
        self.room_title: str = self.room['title']
        self.table_name = users_table_name

    async def new_room(self):
        try:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # get all local rooms
                local_rooms: dict = json.loads(cursor.execute(f"""
                SELECT json_extract(room, '$') FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}';
                """).fetchone()[0])

                # set new room using room-title
                local_rooms[str(id(self.room_title))]: dict = self.room

                # update room column
                cursor.execute(f"UPDATE {self.table_name} SET room='{json.dumps(local_rooms)}' WHERE json_extract(account, '$.username')='{self.username}'")
                database.commit()
                database.close()
                return {"result": room_generated_true}
            else:
                return authentication_result
        # database/table does not exist
        except sqlite3.OperationalError:
            return {"result": account_exists_false}
