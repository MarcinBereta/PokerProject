import random
import ssl
import smtplib
import bcrypt
from email.message import EmailMessage
import shutil

from bson import ObjectId

smtp_server = "smtp.office365.com"

email_sender = 'pokerpythonproject@gmail.com'
email_password = 'pjjbheqmracjoula'


class AuthHandler:
    def __init__(self, db):
        self.db = db
        self.users = self.db["users"]
        self.scores = self.db["scores"]

    def login(self, data):
        user = self.users.find_one({"username": data["userName"]})
        if user is not None:
            if bcrypt.checkpw(data["password"].encode('utf-8'), user["password"]):
                del user["password"]
                user['_id'] = str(user['_id'])
                return {"status": "success", "user": user}
            else:
                return {"status": "error", "message": "Wrong password"}
        else:
            return {"status": "error", "message": "User not found"}

    def register(self, data, file):
        user = list(self.users.find({"$or": [{"name": data["userName"]}, {"email": data["email"]}]}))

        if "@" not in data["email"]:
            return {"status": "error", "message": "Invalid email"}

        if len(user) == 0:
            user = {
                'email': data["email"],
                'username': data["userName"],
                'password': bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt()),
                'avatar': file if file is not None else "default.png",
            }
            self.users.insert_one(user)
            user = self.users.find_one({"username": data["userName"]})
            del user['password']
            user['_id'] = str(user['_id'])
            return {"status": "success", "user": user}
        else:
            return {"status": "error", "message": "User already exists"}

    def forgot_password(self, data):
        user = self.users.find_one({"email": data["email"]})
        del user["_id"]
        if user is None:
            return {"status": "error", "message": "User not found"}
        else:
            code = {
                'email': data["email"],
                'code': random.randint(100000, 999999)
            }
            self.db["codes"].insert_one(code)
            subject = "Poker password reset"
            body = "Your code is: " + str(code["code"])
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = data["email"]
            em['Subject'] = subject
            em.set_content(body)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, data['email'], em.as_string())
                return {"status": "success", "user": user}

    def verify_code(self, data):
        code = self.db["codes"].find_one({"email": data["email"]})
        if code is None:
            return {"status": "error", "message": "Code not found"}
        else:
            if code["code"] == data["code"]:
                return {"status": "success"}
            else:
                return {"status": "error", "message": "Wrong code"}

    def change_password(self, data):
        user = self.users.find_one({"email": data["email"]})
        if user is None:
            return {"status": "error", "message": "User not found"}
        else:
            self.users.update_one({"email": data["email"]}, {
                "$set": {"password": bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())}})
            return {"status": "success"}

    def save_score(self, data):
        user = self.users.find_one({"username": data["userName"]})
        if user is None:
            return {"status": "error", "message": "User not found"}
        else:
            self.scores.insert_one({
                "userId": user["_id"],
                "score": data["score"],
                "username": data["userName"],
            })
            return {"status": "success"}

    def get_user_scores(self, username):
        scores = self.scores.find({"userId": username}).sort("score", -1).limit(10)
        userData = self.users.find_one({"_id": ObjectId(username)})
        del userData["password"]
        userData["_id"] = str(userData["_id"])
        scores = list(scores)
        for score in scores:
            score["_id"] = str(score["_id"])
        return {"status": "success", "scores": scores, "user": userData}

    def update_user_data(self, user_data, file):
        userData = self.users.find_one({"_id": ObjectId(user_data["_id"])})
        print(userData)
        print(user_data)
        if userData is None:
            return {"status": "error", "message": "User not found"}
        else:
            if file is not None:
                if userData["avatar"] != "default.png":
                    shutil.rmtree("images/" + userData["avatar"])
            userAvatar = userData['avatar']
            if file is not None:
                userAvatar = file
            elif user_data["avatar"] is not None:
                userAvatar = user_data["avatar"]
            userPassword = user_data['password']
            if user_data["password"] == "":
                userPassword = userData['password']
            else:
                userPassword = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
            self.users.update_one({"_id": ObjectId(user_data["_id"])}, {
                "$set": {
                    "username": user_data["username"] if user_data["username"] != "" else userData["username"],
                    "email": user_data["email"] if user_data["email"] != "" else userData["email"],
                    "avatar": userAvatar,
                    "password": userPassword
                }
            })
            userData = self.users.find_one({"_id": ObjectId(user_data["_id"])})
            del userData["password"]
            userData["_id"] = str(userData["_id"])
            return {"status": "success", "user": userData}
