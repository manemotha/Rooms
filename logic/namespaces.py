# account authentication
login_namespace: str = "/login"
# generate new rooms account
signup_namespace: str = "/signup"
# change/update account's username
# notice: requires password authentication not token
update_username_namespace: str = "/update/username"
# change/update account's displayName
update_displayname_namespace: str = "/update/displayname"
# change/update account's password
# notice: requires password authentication not token
update_password_namespace: str = "/update/password"
# schedule account for deactivation
# the account is permanently delete after an amount of days
# notice: requires password authentication not token
deactivate_namespace: str = "/deactivate"


# create new room
new_room_namespace: str = "/room/new"
# delete room permanently
delete_room_namespace: str = "/room/delete"
# like room / unlike room
# it toggles like if room not liked & unlike if liked
like_room_namespace: str = "/room/like"


# search room by it title
search_room_by_title_namespace: str = "/search/room/title"
# search room by it _id
# notice: not accessible by front-end application
search_room_by_id_namespace: str = "/search/room/id"
# search user by it _id
search_user_by_id_namespace: str = "/search/user/id"
# find all friend's rooms
# notice: not accessible by front-end application
search_friend_rooms_namespace: str = "/search/friend/rooms"


# follow user / unfollow user
# it toggles follow if user not followed & unfollow if followed
follow_user_namespace: str = "/follow/user"
