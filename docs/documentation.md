## Documentation
This document will tell you more on how the server processes it data from its clients. You will have an idea on how to communicate with the server using `JSON` format data. From creating an Account to sending Direct Messages and creating rooms.
\
\
Reading this documentation you will have enough experience on how to work only with functionalities that have been developed/written by the `contributors` of this Repository.

### Introduction:

The server expects only `JSON` format data from the client as it uses `SQLITE JSON` extension to store the data as JSON format. `Namespace` key is required to tell the server where the client is connecting to. Information like **Username**, **Email**, **Password** is processed before running any function to verify if it meets the requirements **Length** & **Unwanted Symbols**.
\
\
Rooms account uses **Username**, **Email**, **Password** for authentication. Yes every account has it own unique ID but Usernames are secured and used for searching the user's account on **Login** & **Signup**. IDs are used incase the user changes its username then the ID will be used to link to that account instead of declaring account **deactivated**.

## Account... `Class`
This shows you how to play around with Rooms Account like creating,update,removing account.
\
`Method: Signup, Login, Authenticate, UpdateUsername, UpdateEmail, UpdatePassword, Deactivate`


### Signup `method`
For creating an Account the server requires first a JSON with `"namespace": "/signup"`. With this key, the server knows that a user is trying to create a new account. To create a new account it requires `username, email, password` and every data that goes inside a `SQLITE column: Account` which may be `phone, website, personalInfo, basicInfo`.
\
\
For other SQLITE columns like `login, rooms, message, notification ` on signup these columns take `null` as its data and column ID is automatically generated from the account's signup username `id(username)` which generates a unique ID for the account. This ID can not be modified as it represents `rooms, comments, reactions, responses...` authored by the user.

`USERNAME:` Ensure that username has `characters >= 5` and if account with same username exists or not. If an account with same username exists, It returns `account exists: true` or `account generated: true` if an account with username does not exist.

`EMAIL:` Ensure that the Email is a valid **email-address** since the email is used for `Account Security` notifications.

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
For logging into an Account the server requires first a JSON with `"namespace": "/login"`. With this key, the server knows that a user is trying to log into an account. To log in an account it requires `username, email, password`. Email can be used instead of a username incase the user forgets a username. If `username` is empty then the server tries again using the email for authentication.

Logging in using an Email isn't the same as using a username since a username is unique and only one account can have a specific username. But for an email, **multiple** accounts may have the same email and possibly same password too which may raise `security threads` to user accounts `it's recommended to use strong passwords for your accounts`.

So what the server does is to first check how many accounts have a matching email and if over 1 matches the email, the server will return the `id, username, email, displayName` of those accounts for the user to choose from. But if the email only matches one account it will proceed to matching passwords and if a password matches then access will be granted for that user.

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
Is a method used within the server for authenticating every function it goes through like **creating** or **delete** a Room. This is made so the server easily notice any security changes to the account.

For an `example` if a user has two devices logged into his account and one of these devices is not being operated by him. If he decides to change the password then the other device will no longer be authorized, so it won't have access to the user's account.

`Authentication` is a private method that only operates within the server so client connections won't have direct access to it through `namespaces` but they could use `/login` instead.

### Authentication `method`
For deactivating an Account the server requires first a JSON with `"namespace": "/deactivate"`. Now the server knows that you're trying to remove your account and it will require `username, password` for authentication.

To deactivate a Rooms account is just deleting a row in a `SQLITE Database` so it takes less than a minute to finish removing the whole account. 

But as we're hoping there be no hackers, there might be mistakes where a user exposes its authentication data in public and someone tries to deactivate their account.
So to try and prevent this from happening we use a strategy to schedule an account for deactivation after an amount of time.

**Rooms** account takes `30 days` to finally deactivate `permanently`, every user data is deleted and also the username is declared open to be used by another account.
