from .__init__ import *


class Rooms:

    def __init__(self, login_data: dict):
        self.account: dict = login_data
        self.username: str = self.account['username']
        self.email: str = self.account['email']
        self.password: str = self.account['password']
        self.table_name: str = users_table_name

    async def new_room(self, room: dict):
        room_title: str = room['title']

        try:
            database = sqlite3.connect(f'{database_directory}/accounts.db')
            cursor = database.cursor()

            authentication_result = await Account(self.account).authenticate()

            if authentication_result['result'] == account_access_granted:
                # get all local rooms
                local_rooms: dict = json.loads(cursor.execute(f"""
                SELECT json_extract(room, '$') FROM {self.table_name} WHERE json_extract(account, '$.username')='{self.username}';
                """).fetchone()[0])

                # generate random id from room-title
                room_id: str = str(id(room_title))

                # insert id into room_data
                room['id']: str = room_id

                # set new room KEY using room-id
                local_rooms[room_id]: dict = room

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
