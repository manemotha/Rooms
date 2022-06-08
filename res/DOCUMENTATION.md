## Documentation
This document will tell you more on how the server processes it data from its clients.

### Introduction:

The server expects only `JSON` format data from the client as it uses `SQLITE JSON` extension to store the data as JSON format. `Namespace` key is required to tell the server where the client is connecting to. Information like **Username**, **Email**, **Password** is processed before running any function to verify if it meets the requirements **Length** & **Unwanted Symbols**.
\
\
Rooms account uses **Username**, **Email**, **Password** for authentication. Yes every account has it own unique ID but Usernames are secured and used for searching the user's account on **Login** & **Signup**. IDs are used incase the user changes its username then the ID will be used to link to that account instead of declaring account **deactivated**.

## Account
This shows you how to play around with Rooms Account like creating,update,removing account.
\
`Method: Signup, Login, Authenticate, UpdateUsername, UpdateEmail, UpdatePassword, Deactivate`

### Signup
For creating an Account the server requires first a JSON with `"namespace": "/signup"`. With this key, the server knows that a user is trying to create a new account. To create a new account it requires `username, email, password` and every data that goes inside a `SQLITE column: Account` which may be `phone, website, personalInfo, basicInfo`.

`USERNAME:` Ensure that username has `characters >= 5` and if account with same username exists or not. If an account with same username exists, It returns `account exists: true` or `account generated: true` if an account with username does not exist.

`EMAIL:` Ensure that the Email is a valid **email-address** because the email is used for `Account Security` notifications.

`PASSWORD:` Ensure that password has `characters >= 8` and hash the password using `Bcrypt` before storing it onto the database.

#### JSON Example:

    {
        "namespace":"/signup",
        "account":{
            "email":"user.email@gmail.com",
            "username":"john",
            "password":"12345678",
            "phone":"483 598 234",
            "website": "johnwebsite.com",
            "displayName":"JohnWick",
            "bio":"Hi! I am John Wick and i wear formal all time",
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
