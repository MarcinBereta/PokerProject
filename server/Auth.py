import random
import ssl
import smtplib
import bcrypt
from email.message import EmailMessage
import shutil

smtp_server = "smtp.office365.com"

email_sender = 'pokerpythonproject@gmail.com'
email_password = 'pjjbheqmracjoula'


class AuthHandler:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["users"]

    def login(self, data):
        user = self.collection.find_one({"name": data["name"]})
        if user is not None:
            if bcrypt.checkpw(data["password"].encode('utf-8'), user["password"]):
                del user["password"]
                del user["_id"]
                return {"status": "success", "user": user}
            else:
                return {"status": "error", "message": "Wrong password"}
        else:
            return {"status": "error", "message": "User not found"}

    def register(self, data, file):
        user = self.collection.find_one({"name": data["name"]})
        if "@" not in data["email"]:
            return {"status": "error", "message": "Invalid email"}

        if user is None:
            #Save data['file'] to server
            hashedName = bcrypt.hashpw(data["name"].encode('utf-8'), bcrypt.gensalt())
            user = {
                'email': data["email"],
                'display_name': data["displayName"],
                'name': data["name"],
                'img': file,
                'password': bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
            }
            self.collection.insert_one(user)
            del user["password"]
            del user["_id"]
            return {"status": "success", "user": user}
        else:
            return {"status": "error", "message": "User already exists"}

    def forgot_password(self, data):
        user = self.collection.find_one({"email": data["email"]})
        print(user)
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
                print("Email sent")
                print(email_sender)
                print(data['email'])
                return {"status": "success", "user":user}
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
        user = self.collection.find_one({"email": data["email"]})
        if user is None:
            return {"status": "error", "message": "User not found"}
        else:
            self.collection.update_one({"email": data["email"]}, {"$set": {"password": bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())}})
            return {"status": "success"}