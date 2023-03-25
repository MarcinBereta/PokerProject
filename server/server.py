import os

from pymongo import MongoClient
from flask import Flask, render_template, request

app = Flask(__name__)
cluster = "mongodb+srv://Mardorus:PokerAGH@poker.gmn3mgg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cluster)
from Auth import AuthHandler


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/login')
def login():
    return "login"


@app.route('/login', methods=['POST'])
def handleLogin():
    loginData = request.form
    return loginHandler.login(loginData)


@app.route('/register', methods=['POST'])
def handleRegister():
    registerData = request.form
    if 'file' not in request.files:
        return loginHandler.register(registerData, None)
    else:
        file = request.files['file']
        file.save(os.path.join('./images/', file.filename))
        return loginHandler.register(registerData, file.filename)

@app.route('/forgot_password', methods=['POST'])
def handleForgotPassword():
    forgotPasswordData = request.form
    return loginHandler.forgot_password(forgotPasswordData)


if __name__ == "__main__":
    # SocketServer.runSockets()
    db = client["poker"]
    loginHandler = AuthHandler(db)
    app.run(debug=True, port=5000, host='127.0.0.1')
