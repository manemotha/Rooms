from .__init__ import *

# store connected users using "_id"
# every user's websocket connection will be stored here and removed on disconnection
connected_accounts: dict = {
    # "_id": websocket
}
