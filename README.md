# ROOMS
______________________
Is a realtime websocket server for a room / group like chat application. Groups are referred to as **Rooms** and users as **Mates** or **RoomMates** if they have a mutual room.

### `Functionality`
* Let users create topics and let other **Mates** join in for a **Real-Time** Text & Audio conversation.
* Topics can be of mostly **Text**,**Image** and **Video**.
* Instead of talking to each other. Users can track most information about their RoomMates & Followers like `Age, Race, Gender, Height, Weight, Language, Country, RelationshipStatus, Hobbies, Health...` Yes most of this information is personal so the user can either make it **Public** or **Private** for other **Roommates**.
* Exchange direct messages if willing to communicate outside the Room.

## Documentation
______________________
This document will tell you more on how the server processes it data from its clients. You will have an idea on how to communicate with the server using `JSON` format data. From creating an Account to sending Direct Messages and creating rooms.
\
\
Reading this documentation you will have enough experience on how to work only with functionalities that have already been pushed by the `maintainers` of this Repository.

### Introduction:

The server expects only `JSON` format data from the client as it uses `MongoDB Database` to store data. `Namespace` key is required to tell the server where the client is connecting to. Information like **Username**, **Email**, **Password** is processed before running any function to verify if it meets the requirements **Length** & **Unwanted Symbols**.
\
\
Rooms account uses **Username**, **Email**, **Password** for authentication. Yes every account has it own unique ID but Usernames are secured and used for searching the user's account on **Login** & **Signup**. IDs are used incase the user changes its username then the ID will be used to link to that account instead of declaring account **deactivated**.

## Account... `Class`
This shows you how to play around with Rooms account's CRUD operations.
\
`Method: Signup, Login, Authenticate, UpdateUsername, UpdateEmail, UpdatePassword, Follow, Deactivate`

### Signup `method`
______________________
For creating an Account the server requires first a JSON payload with `"namespace": "/signup"`. With this key, the server knows that a user is trying to create a new account. To create a new account it requires `username, email, password` and every data that will be part of the user's account which may be `phone, website, personalInfo, basicInfo`.
\
\
For other MongoDB keys like `login, rooms, message, notification ` on signup these keys are `null` as it's data isn't specified yet and the account uses `MongoDB _id` as its unique ID. This ID can not be modified as it represents `rooms, comments, reactions, responses...` authored by the user.

`USERNAME:` Ensure that username has `characters >= 5`, Ensure it's `lowercase` and if account with same username exists or not. If an account with same username exists, It returns `account exists: true` or `account generated: true` if an account with username did not exist.

`EMAIL:` Ensure that the Email is a valid **email-address** since the email is used for `Account Notifications`.

`PASSWORD:` Ensure that password has `characters >= 8` and hash the password using `Bcrypt` before storing it onto the database.

#### JSON Example:

    {
        "namespace":"/signup",
        "account":{
            "email":"wilson.wick@gmail.com",
            "username":"wilson",
            "password":"12345678",
            "phone":"483 598 234",
            "website": "wilsonwebsite.com",
            "displayName":"WilsonWick",
            "bio":"Hi! I am Wilson Wick and i wear formal all time",
            "personalInfo":{
                    "health":["flu","insomnia"],
                    "hobbies":["coding","movies","eating"]},
            "basicInfo":{
                    "sex":"male",
                    "race":"white",
                    "height":"48.0",
                    "weight":"12.9",
                    "birthDate":"2001/05/12",
                    "interestedInMen":"false",
                    "interestedInWomen":"true",
                    "maritalStatus": "single"}
        }
    }

### Login `method`
______________________
For logging into an Account the server requires first a JSON payload with `"namespace": "/login"`. With this key, the server knows that a user is trying to log into an account. To log in an account it requires `username, email, password`. Email can be used instead of a username incase the user forgets a username. If `username` is empty then the server tries using the email for authentication.

Logging in using an Email isn't the same as using a username since a username is unique and only one account can have a specific username. But for an email, **multiple** accounts may have the same email and possibly same password too which may raise `security threads` to user accounts. It's recommended to use strong passwords for your accounts.

So what the server does is to first check how many accounts have a matching email and if over 1 account matches the email, the server will return the `id, username, email, displayName` of those accounts for the user to choose from. But if the email only matches one account it will proceed to matching passwords and if a password matches then access will be granted for that user.

#### JSON Example:

    {
        "namespace":"/login",
        "account":{
            "email":"user.wick@gmail.com",
            "username":"wilson",
            "password":"12345678"
        }
    }
### Authentication `method`
______________________
Is a method used within the server for authenticating every function it goes through like **creating** or **delete** a Room. This is made so the server easily notice any security changes to the account.

For an `example` if a user has two devices logged into his account and one of these devices is not being operated by him. If he decides to change the password then the other device will no longer be authorized, so it won't have access to the user's account.

`Authentication` is a private method that only operates within the server so client connections won't have direct access to it through `namespaces` but can use `"namespace": "/login"` instead.
### UpdateDisplayName `method`
______________________
DisplayName can be modified to any word with any character and or emoji. But it can not be empty, It'll at least require 1 character. 

#### JSON Example:

    {
        "namespace":"/update/displayname",
        "updateDisplayName":"Wilson Python Dev 🙂",
        "account":{
            "email":"user.wick@gmail.com",
            "username":"wilson",
            "password":"12345678",
            "displayName":"Wilson Wick",
        }
    }
### UpdateUsername `method`
______________________
Updating a username is easy as logging in. `"namespace":"/update/username"` is used and `"updateUsername":"wilson2022"` is the going to be the new username for this account.

For security purposes the new username will go through same security as the old username when signing up like checking its `length`, checking if it's the same as the old username and checking if any account exists with the same username.

#### JSON Example:

    {
        "namespace":"/update/username",
        "updateUsername":"wilson2022",
        "account":{
            "email":"user.wick@gmail.com",
            "username":"wilson",
            "password":"12345678"
        }
    }
### UpdatePassword `method`
______________________
Updating a password is easy as updating a username. `"namespace":"/update/password"` is used and `"updateUsername":"12345678wilson"` is the going to be the new password for this account.

For security purposes the new password will go through same security as the old password when signing up like checking its `length` and checking if it's not the same as the old password.

#### JSON Example:

    {
        "namespace":"/update/password",
        "updateUsername":"12345678wilson",
        "account":{
            "email":"user.wick@gmail.com",
            "username":"wilson",
            "password":"12345678"
        }
    }
### Deactivate`method`
______________________
For deactivating an Account the server requires first a JSON payload with `"namespace": "/deactivate"`. Now the server knows that you're trying to remove your account and it will require `username, password` for authentication.

Deactivating a Rooms account is basically deleting a `MongoDB Document` so it takes less than a minute to finish removing the whole account. 

But as we're hoping there be no hackers, there might be mistakes where a user exposes his security information in public and someone tries to deactivate their account.
So to try and prevent this from happening we use a strategy to schedule an account for deactivation after an amount of time.

**Rooms** account takes `30 days` to finally deactivate `permanently`, every user data is deleted and also the username is declared available to be used by another account.
