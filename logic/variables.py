# this host is for a local MongoDB server
# change this host to your MongoDB host address
database_uri = "mongodb://localhost:27017"

# namespaces
unknown_namespace: str = "unknown namespace"

# account & account-dir
account_generated_true: str = "account generated: true"
account_deactivated_true: str = "account deactivate: true"
account_exists_true: str = "account exists: true"
account_exists_false: str = "account exists: false"

# account update
account_updateUsername_exists_true: str = "account updateUsername exists: true"
account_username_updated_true: str = "username updated: true"
account_displayName_updated_true: str = "displayName updated: true"
account_password_update_true: str = "password updated: true"
account_updatePassword_match_oldPassword: str = "password update: updatePassword match oldPassword"

# access
account_access_granted: str = "access granted"
account_access_denied_password: str = "access denied: incorrect password"
account_access_denied_passwordhash: str = "access denied: password not hashed \"account removed\""
# character
username_unwanted_character: str = "unwanted character in username"

# this variable is the name of the MongoDB collection created -
# when you first create an account to the server
users_table_name: str = "users"
# this variable is the name of the database created -
# when you connect to MongoDB server
users_database_name: str = "demo"


# rooms
room_generated_true: str = "room generated: true"
room_exists_false: str = "room exists: false"
room_deleted_true: str = "room deleted: true"
room_match_found: str = "room match found: true"

# room react
liked_room_true: str = "liked room"
liked_room_false: str = "unliked room"


# system/search
user_match_found_true: str = "user match found: true"
user_match_found_false: str = "user match found: false"

# system/follow
following_account_exists_false: str = "following account exists: false"
followed_user: str = "followed user"
unfollowed_user: str = "unfollowed user"
following_account_matches_current_account: str = "userId matches current user id"
